# ReCarmend System Sequence Diagram (Detailed with Function Calls)

## Complete Flow with Function Names and Return Values

### Components:
- **User**: Active throughout entire session (lifeline spans full diagram)
- **Frontend**: React/Vite application
- **Backend**: Flask API server
- **Cohere AI**: Natural language processing
- **Supabase**: PostgreSQL database
- **Pexels API**: Image search service

---

## Main Search Flow

```
User (lifeline: ┃───────────────────────────────────────────────┃)
                 │
                 │ 1. searchCars(query: "red SUV under $30k")
                 ├───────────────────────────────────────────────>
                 │
Frontend         │ 2. POST /api/search
(lifeline:       │    search(query)
      ┃──────────┼───────────────────────────────────────────────>
      │          │
      │          │
Backend          │ 3. co.chat()
(lifeline:       │    aiSearch(prompt)
      ┃──────────┼───────────────────────────────────────────────>
      │          │
      │          │
Cohere           │
(lifeline:       │
      ┃──────────┼───────────────────────────────────────────────>
      │          │
      │          │ 4. return parsed_params
      │          │    {make: null, price: 30000, bodyType: "SUV"}
      │<──────────┼─────────────────────────────────────────────── (dotted)
      │          │
      │          │ 5. sortDB()
      │          │    query.select('*').limit(10).execute()
      │──────────┼───────────────────────────────────────────────>
      │          │
Supabase         │
(lifeline:       │
      ┃──────────┼───────────────────────────────────────────────>
      │          │
      │          │ 6. return cars[]
      │          │    [{id, make, model, year, ...}, ...]
      │<──────────┼─────────────────────────────────────────────── (dotted)
      │          │
      │          │ LOOP: For each car (max 10)
      │          │ 7. get_car_image_url(make, model, year, color)
      │          │    requests.get(search_url)
      │──────────┼───────────────────────────────────────────────>
      │          │
Pexels           │
(lifeline:       │
      ┃──────────┼───────────────────────────────────────────────>
      │          │
      │          │ 8. return image_url
      │          │    "https://images.pexels.com/..."
      │<──────────┼─────────────────────────────────────────────── (dotted)
      │          │ END LOOP
      │          │
      │          │ 9. format_car_results(cars)
      │          │    [internal processing]
      │──────────>│
      │          │
      │          │ 10. return jsonify()
      │          │     {cars: [...], count: 10, hasMore: true}
      │<──────────┼─────────────────────────────────────────────── (dotted)
      │          │
      │          │ 11. normalizeCar(car)
      │          │    [internal processing]
      │──────────>│
      │          │
      │          │ 12. return render CarCard[]
      │          │     [Display car cards]
      │<──────────┼─────────────────────────────────────────────── (dotted)
      │          │
```

---

## Function Call Details

### Step 1: User → Frontend
- **Function**: `searchCars(query: string)`
- **Location**: `View/src/services/api.ts`
- **Arrow**: Solid (→)

### Step 2: Frontend → Backend
- **Function**: `POST /api/search`
- **Handler**: `search()` in `api_server.py`
- **Arrow**: Solid (→)

### Step 3: Backend → Cohere
- **Function**: `co.chat()`
- **Internal**: `aiSearch(prompt)`
- **Arrow**: Solid (→)

### Step 4: Cohere → Backend
- **Return**: `parsed_params` dictionary
- **Arrow**: Dotted (-->>) - RETURN VALUE

### Step 5: Backend → Supabase
- **Function**: `sortDB()`
- **Method**: `query.select('*').limit(10).execute()`
- **Arrow**: Solid (→)

### Step 6: Supabase → Backend
- **Return**: `cars[]` array
- **Arrow**: Dotted (-->>) - RETURN VALUE

### Step 7: Backend → Pexels (LOOP)
- **Function**: `get_car_image_url(make, model, year, color)`
- **Method**: `requests.get(search_url)`
- **Arrow**: Solid (→)
- **Loop**: Repeats for each car (max 10)

### Step 8: Pexels → Backend (LOOP)
- **Return**: `image_url` string
- **Arrow**: Dotted (-->>) - RETURN VALUE
- **Loop**: Repeats for each car

### Step 9: Backend → Backend (Self-call)
- **Function**: `format_car_results(cars)`
- **Arrow**: Solid self-call (→)

### Step 10: Backend → Frontend
- **Return**: `jsonify({cars, count, hasMore})`
- **Arrow**: Dotted (-->>) - RETURN VALUE

### Step 11: Frontend → Frontend (Self-call)
- **Function**: `normalizeCar(car)`
- **Arrow**: Solid self-call (→)

### Step 12: Frontend → User
- **Return**: `render CarCard[]`
- **Arrow**: Dotted (-->>) - RETURN/DISPLAY

---

## Figma Implementation Notes

1. **Lifelines**: Draw vertical dashed lines for each component
2. **User Lifeline**: Should span entire diagram (top to bottom)
3. **Activation Boxes**: Draw vertical rectangles on lifelines when component is active
4. **Solid Arrows**: Use for function calls (→)
5. **Dotted Arrows**: Use for return values (-->>)
6. **Loop Notation**: Draw a rectangle around steps 7-8 with label "LOOP: For each car (max 10)"
7. **Self-calls**: Draw arrows that loop back to same component for internal processing

