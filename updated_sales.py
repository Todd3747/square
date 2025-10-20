#!/usr/bin/env python3

import sys, os
import re
import logging
import logging.handlers
import subprocess
import time
import calendar
import json
import datetime
from datetime import datetime
from dateutil.tz import tzutc, tzlocal
import pytz
from pprint import pprint
from decimal import Decimal
import configparser
from square.client import Square, SquareEnvironment

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'init.ini')

if not os.path.exists(config_path):
    print(f"Error: Configuration file not found at {config_path}")
    print("Please create init.ini with the following structure:")
    print("[square]")
    print("token = YOUR_SQUARE_ACCESS_TOKEN_HERE")
    print("location_id = YOUR_LOCATION_ID_HERE") 
    print("pasty = YOUR_PRODUCT_VARIATION_ID_HERE")
    print("donation = YOUR_DONATION_ITEM_ID_HERE")
    sys.exit(1)

config.read(config_path)

# Validate required configuration
required_keys = ['token', 'location_id', 'pasty', 'donation']
for key in required_keys:
    if not config.has_option('square', key):
        print(f"Error: Missing required configuration key '{key}' in [square] section")
        sys.exit(1)

# Initialize Square client with config values
client = Square(
    token=config.get('square', 'token'),
    environment=SquareEnvironment.PRODUCTION,
)

logfile        = "output.log"
curPID         = os.getpid()

# Catalog IDs for tracking from config
PRODUCT_VARIATION_ID = config.get('square', 'pasty')    # Product variation ID (legacy config key name)
DONATION_ID          = config.get('square', 'donation') # Donation item ID
LOCATION_ID          = config.get('square', 'location_id') # Square location ID

def main():
  if len(sys.argv) == 2:
    q_date = sys.argv[1]
  else:
    printf("\n\tUSAGE: %-5s <query_date ie. 2025-10-13>\n\n",sys.argv[0])
    sys.exit()

  # Fetch all orders (handle pagination)
  all_orders = []
  cursor = None
  
  try:
    while True:
      if cursor:
        result = client.orders.search(
          location_ids=[
            LOCATION_ID
          ],
          query={
            "filter": {
              "date_time_filter": {
                "created_at": {
                  "start_at": q_date+"T00:00:00-05:00",
                  "end_at": q_date+"T23:59:59-05:00"
                  }
                }
              }
            },
          cursor=cursor
        )
      else:
        result = client.orders.search(
          location_ids=[
            LOCATION_ID
          ],
          query={
            "filter": {
              "date_time_filter": {
                "created_at": {
                  "start_at": q_date+"T00:00:00-05:00",
                  "end_at": q_date+"T23:59:59-05:00"
                  }
                }
              }
            }
        )
      
      if hasattr(result, 'orders') and result.orders:
        all_orders.extend(result.orders)
      
      # Check if there are more pages
      if hasattr(result, 'cursor') and result.cursor:
        cursor = result.cursor
      else:
        break
        
  except Exception as e:
    print(f"Error searching orders: {e}")
    sys.exit(1)

  printf("================================================================================================================================================================\n")
  printf("PRODUCT SALES & DONATIONS REPORT - %s\n", q_date)
  printf("================================================================================================================================================================\n")
  printf("%-28s %-30s %-35s %-16s %8s %12s %10s\n", "Date/Time", "Customer", "Email", "Phone", "Products", "Donations", "Total")
  printf("================================================================================================================================================================\n")

  orders = all_orders

  if not orders:
    print("No Sales")
    sys.exit()

  total_products = 0
  total_donations = 0.00
  total_sales = 0.00
  order_count = 0

  printf("DEBUG: Total orders returned: %d\n", len(orders))

  for element in orders:
     try:
       # Skip draft orders - they haven't been paid
       if hasattr(element, 'state') and element.state == 'DRAFT':
         printf("DEBUG: Skipping DRAFT order\n")
         continue
       
       # Check if order has tenders (payments)
       tenders = element.tenders if hasattr(element, 'tenders') and element.tenders else []
       if not tenders:
         printf("DEBUG: Skipping order with no tenders\n")
         continue
       
       # Check if payment was captured
       payment_captured = False
       for tender in tenders:
         if hasattr(tender, 'type') and tender.type == 'CARD':
           if hasattr(tender, 'card_details') and tender.card_details:
             if hasattr(tender.card_details, 'status') and tender.card_details.status == 'CAPTURED':
               payment_captured = True
               break
       
       if not payment_captured:
         printf("DEBUG: Skipping order with no captured payment\n")
         continue
       
       # Get order details
       orderDate = element.created_at if hasattr(element, 'created_at') else None
       if not orderDate:
         continue
         
       dateTime = convertTimeToLocal(orderDate)
       
       try:
         customer = element.fulfillments[0].pickup_details.recipient.display_name
         email    = element.fulfillments[0].pickup_details.recipient.email_address
         phone    = element.fulfillments[0].pickup_details.recipient.phone_number
       except:
         customer = 'N/A'
         email = 'N/A'
         phone = 'N/A'

       products  = 0
       donation  = 0.00
       total     = 0.00

       # Extract product and donation quantities/amounts
       if hasattr(element, 'line_items') and element.line_items:
         for item in element.line_items:
           if hasattr(item, 'catalog_object_id') and item.catalog_object_id == PRODUCT_VARIATION_ID:
             products = int(item.quantity)
           elif hasattr(item, 'catalog_object_id') and item.catalog_object_id == DONATION_ID:
             donation = int(item.total_money.amount) / 100

       # Get total order amount
       if hasattr(element, 'total_money') and element.total_money:
         total = int(element.total_money.amount) / 100

       # Only display if order contains products or donations
       if products > 0 or donation > 0:
         printf("%-28s %-30s %-35s %-16s %8d %12.2f %10.2f\n", 
                str(dateTime), customer[:30], email[:35], phone, products, donation, total)
         
         total_products += products
         total_donations += donation
         total_sales += total
         order_count += 1

     except Exception as e:
       printf("Error processing order: %s\n", str(e))
       pass

  # Print summary
  printf("================================================================================================================================================================\n")
  printf("SUMMARY:\n")
  printf("  Total Orders:     %d\n", order_count)
  printf("  Total Products:   %d\n", total_products)
  printf("  Total Donations:  $%.2f\n", total_donations)
  printf("  Total Sales:      $%.2f\n", total_sales)
  printf("================================================================================================================================================================\n\n")

  sys.exit()


def convertTimeToLocal(time):
    foo = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Central'))
    return(foo)


def printf(format, *args):
   sys.stdout.write(format % args)
   return;


if __name__ == "__main__":
  main()
