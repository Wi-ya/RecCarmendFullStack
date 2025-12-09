# -*- coding: utf-8 -*-
"""
ReCarmend - Car Recommendation System
Converts user preferences into car recommendations using filtered search or AI-powered search.
"""

import os
import warnings
import random
# Suppress Pydantic V1 compatibility warning from cohere library
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

import cohere
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Configure pandas to display all columns and full content
pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.max_colwidth", None)  # Show full content in each column
pd.set_option("display.width", None)  # Auto-detect terminal width
pd.set_option("display.max_rows", None)  # Show all rows
def sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType):
  """
  Query the database for cars matching the specified criteria.
  Returns up to 10 matching results.
  """
  userDB = []
  
  # Normalize input values
  color = color.lower() if color and color.lower() not in ["null", ""] else None
  make = make.lower() if make and make.lower() not in ["null", ""] else None
  model = model.lower() if model and model.lower() not in ["null", ""] else None
  carType = carType.lower() if carType and carType.lower() not in ["null", ""] else None
  
  # Build the query with filters
  query = supabase.table('CarListings').select('*')
  
  # Apply numeric filters
  if maximumPrice > 0:
    query = query.lte('price', maximumPrice)
  if maximumMileage > 0:
    query = query.lte('mileage', maximumMileage)
  if minYear > 0:
    query = query.gte('year', minYear)
  if maxYear > 0:
    query = query.lte('year', maxYear)
  
  # Apply text filters (case-insensitive search)
  if color:
    query = query.ilike('color', f'%{color}%')
  if make:
    query = query.ilike('make', f'%{make}%')
  if model:
    query = query.ilike('model', f'%{model}%')
  
  # Handle carType - try both possible column names
  if carType:
    # Try body_type column first (most likely column name)
    try:
      query_with_cartype = query.ilike('body_type', f'%{carType}%')
      response = query_with_cartype.limit(10).execute()
      if response.data and len(response.data) > 0:
        return response.data
    except Exception as e:
      # If body_type fails, try carType column
      try:
        query_with_cartype = query.ilike('carType', f'%{carType}%')
        response = query_with_cartype.limit(10).execute()
        if response.data and len(response.data) > 0:
          return response.data
      except Exception as e2:
        # If both fail, continue without carType filter but warn user
        print(f"Warning: Could not filter by car type '{carType}', showing all types")
  
  # Execute query (either no carType filter, or carType filter failed)
  try:
    response = query.limit(10).execute()
    userDB = response.data if response.data else []
  except Exception as e:
    print(f"Error querying database: {e}")
    return []
  
  return userDB




# cleanDB function removed - data is already cleaned in the database

def safeInt(x, default = 0):
  try:
    return int(float(str(x).replace(",", "")))
  except:
    return default


def filteredSearch():
  print("If these filters are not relevant to you please input -1")
  maximumPrice = int(input("What is the max acceptable price: ") or -1)
  maximumMileage = int(input("What is the max acceptable mileage: ") or -1)
  minYear = int(input("What is the earliest year : ") or -1)
  maxYear = int(input("What is the latest year (put the current year if this filter is not inportant to you): ") or 2026)

  color = (input("What is the desired color: ") or "null").lower()
  make = (input("What is the desired maker: ") or "null").lower()
  model = (input("What is the desired model: ") or "null").lower()
  carType = (input("What is the desired car type (the only valid inputs for this are Convertible, Coupe, Hatchback, Hybrid, Sedan, SUV, Minivan, Pickup Truck) an answer other than one of these will produce incorrect results: ") or "null").lower() #(Convertible, Coupe, Hatchback, Hybrid, Sedan, SUV, Minivan, Pickup Truck)
  results = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType)
  return results

def aiSearch():
  prompt = input("describe the kind of car you would want: ")
  response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt + "Please take the prompt above and isolate the desired model, make, year range, maximum price, color, maximum mileage, and car type.If the prompt given does not relate to cars please ignore the prompt entirely and print nothing more than this prompt does not relate to cars.If An exact color is not specified please return it as null, a color should be given if it is a very general color ex(red orange yellow green blue, black, white, silver NOT matte black or platinum silver) if the given prompt does not include information for Color, Make or Model and car types please return it as 'null'.If the prompt does not specify an exact number for miles or price use judgement of what the prompt seems to want and give a number for example if asked for a car with low mileage do NOT return 'low mileage' return something like 5000. If multiple makes are given please select only 1. possible car types are Convertible, Coupe, Hatchback, hybrid, Sedan, SUV, Minivan, Pickup Truck, if one of these is not specified please return null. If it does not include information for Maximum Price, MAximum Mileage, or Min year please return it as 0, for max year please return the current year(2026) Do not include any addition text.The current year is 2026. Please format the output as Maximum Price: Maximum Mileage: Car type: Color: Make: Model: Minimum Year: Maximum Year: "}]
        )
  # Handle Cohere API response - check different possible response formats
  try:
    if hasattr(response, 'text'):
      rawText = response.text
    elif hasattr(response, 'message') and hasattr(response.message, 'content'):
      if isinstance(response.message.content, list) and len(response.message.content) > 0:
        rawText = response.message.content[0].text if hasattr(response.message.content[0], 'text') else str(response.message.content[0])
      else:
        rawText = str(response.message.content)
    else:
      rawText = str(response)
  except Exception as e:
    print(f"Error parsing Cohere response: {e}")
    rawText = ""
  parsed = {}
  for line in rawText.split("\n"):
    if ":" in line:
      key,value = map(str.strip, line.split(":", 1))
      parsed[key.strip()] = value.strip()
  maximumPrice = safeInt(parsed.get("Maximum Price", 0))
  maximumMileage = safeInt(parsed.get("Maximum Mileage", 0))
  minYear = safeInt(parsed.get("Minimum Year", 0))
  maxYear = safeInt(parsed.get("Maximum Year", 2026))

  color = parsed.get("Color", "Null")
  make = parsed.get("Make", "Null")
  model = parsed.get("Model", "Null")

  carType = parsed.get("Car type", "Null")

  print("Based on your prompts this is the requirements the system is looking for")
  print(rawText)
  results = sortDB(maximumPrice, maximumMileage, color, make, model, minYear, maxYear, carType)
  return results


# Connect to Supabase database
DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

if not DB_URL or not DB_API_KEY:
    raise ValueError(
        "Missing Supabase credentials in .env file. "
        "Please add:\n"
        "DB_URL=https://your-project.supabase.co\n"
        "DB_API_KEY=your-service-role-key\n\n"
        "Get these from: Supabase Dashboard → Settings → API"
    )

try:
    print("Connecting to Supabase database...")
    supabase: Client = create_client(DB_URL, DB_API_KEY)
    print("✅ Connected to Supabase database")
except Exception as e:
    raise ConnectionError(f"Failed to connect to Supabase: {e}")




# Get Cohere API key from .env file for security
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError(
        "COHERE_API_KEY not found in .env file. "
        "Please create a .env file in the Controller directory with: COHERE_API_KEY=your-api-key"
    )

co = cohere.ClientV2(cohere_api_key)


userDB = []


maximumPrice = -1
maximumMileage = -1
color = 'Null'
make = 'Null'
model = 'Null'
minYear = -1
maxYear = 2026
carType = 'Null'
inputType = 0
running = True
while running:
  while inputType not in(1, 2, 3, 4):
    inputType = int(input("1: Filter search, 2: AI Search 3: Remove a recommendation 4: exit the program(1/2/3/4): "))
    if(inputType == 1):
      results = filteredSearch()
      userDB.extend(results)
      results = 0;
    elif(inputType == 2):
      results = aiSearch()
      userDB.extend(results)
      results = 0;
    elif(inputType ==3):
      if len(userDB) == 0:
        print("You have no recomendations to remove!")
      else:
        print("\nCurrent Recommendations:")
        df = pd.DataFrame(userDB)

        try:
          toRemove = int(input("\nEnter the index number to remove"))
          #toRemove - 1
          if 0 < toRemove < len(userDB):
            removed = userDB.pop(toRemove)
          else:
            print("Invalid index")
        except ValueError:
          print("Please enter a valid number")

    elif(inputType == 4):
      running = False
      break
  print("\ncurrent recommendations are\n")
  if userDB:
    df = pd.DataFrame(userDB)
    # Select and order the most important columns for display
    important_cols = ['year', 'make', 'model', 'price', 'mileage', 'color', 'body_type', 'url']
    # Only show columns that exist in the data
    display_cols = [col for col in important_cols if col in df.columns]
    if display_cols:
      print(df[display_cols].to_string(index=False))
    else:
      print(df.to_string(index=False))
  else:
    print("No recommendations found.")
  inputType = 0

#Wi ya webscraping goes here,  I THINK WE SHOULDP PUT THEM IN DIFFERENT FOLDERS, SEPERATION ON CONCERNS BLAH BALH