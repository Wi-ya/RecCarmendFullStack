# User Limits: Static vs Dynamic Requirements

## Static vs Dynamic Requirements

### Static Requirements (Fixed Values)
- **Definition**: Fixed, unchanging numerical values that the system must meet
- **Example**: "The system must support 1000 concurrent users"
- **Use Case**: When you need a guaranteed minimum capacity

### Dynamic Requirements (Variable Values)
- **Definition**: Values that change based on external factors (API plans, tiers, time periods)
- **Example**: "The system must support X users based on current API tier"
- **Use Case**: When limits depend on service provider plans

## Recommendation: Document as DYNAMIC Requirements

### Why Dynamic?

API limits are **dynamic** because they depend on:
1. **Service Tier**: Free vs Paid plans have different limits
2. **Provider Changes**: API providers can update limits
3. **Time Periods**: Per hour, per day, per month limits
4. **Usage Patterns**: Limits vary by operation type

### How to Document

#### Option 1: Dynamic Requirements (Recommended)

```
NFR-1: API Rate Limiting (Dynamic)
- The system must handle API rate limits based on current service tier
- Cohere AI: Minimum 100 requests/month (free tier), scalable to 10,000+ (paid)
- Pexels API: 200 requests/hour (free tier), scalable to unlimited (paid)
- Supabase: 2 GB bandwidth/month (free tier), scalable to 250 GB+ (paid)
- System must gracefully handle rate limit errors with fallback mechanisms
```

#### Option 2: Static Minimum Requirements

```
NFR-1: Minimum API Capacity (Static)
- The system must support at least 50 concurrent users
- The system must process at least 100 searches per hour
- The system must handle at least 1,000 database queries per day
```

#### Option 3: Hybrid Approach (Best for Requirements Docs)

```
NFR-1: API Rate Limiting (Hybrid)
- Static Minimum: System must support at least 50 concurrent users
- Dynamic Current: Current implementation supports:
  * Cohere AI: 100-1000 requests/month (based on free tier)
  * Pexels API: 200 requests/hour (free tier)
  * Supabase: 2 GB bandwidth/month (free tier)
- Scalability: System must be upgradeable to support 10,000+ users/month
- Error Handling: System must gracefully degrade when limits are reached
```

## Recommended Format for Your Requirements Document

### Non-Functional Requirements (NFR)

**NFR-1: API Rate Limiting (Dynamic)**
- **Type**: Dynamic (depends on service tier)
- **Current Limits** (Free Tier):
  - Cohere AI: ~100-1000 requests/month
  - Pexels API: 200 requests/hour
  - Supabase: 2 GB bandwidth/month, unlimited API requests
- **Scalability**: System must support upgrade to paid tiers for increased capacity
- **Error Handling**: System must implement fallback mechanisms (e.g., fallback images when Pexels rate limit reached)

**NFR-2: Concurrent User Support (Static)**
- **Type**: Static
- **Requirement**: System must support minimum 10 concurrent users
- **Current Capacity**: Limited by API rate limits (see NFR-1)
- **Scalability**: Can scale to 100+ concurrent users with paid API tiers

**NFR-3: Response Time (Static)**
- **Type**: Static
- **Requirement**: 
  - AI search: < 5 seconds
  - Filter search: < 2 seconds
  - Image loading: < 3 seconds (with fallback)

**NFR-4: Database Capacity (Dynamic)**
- **Type**: Dynamic (depends on Supabase tier)
- **Current**: 500 MB storage (free tier)
- **Scalability**: Upgradeable to 8 GB+ (paid tiers)

## Summary

**For Requirements Documentation:**

1. **API Limits** → Document as **DYNAMIC** requirements
   - Specify current tier limits
   - Note scalability options
   - Include error handling requirements

2. **Performance Targets** → Document as **STATIC** requirements
   - Response times
   - Minimum concurrent users
   - Uptime requirements

3. **Capacity Limits** → Document as **HYBRID**
   - Static minimum acceptable
   - Dynamic current implementation
   - Scalability path

## Example Requirements Statement

```
NFR-5: External API Integration Limits (Dynamic)
The system integrates with third-party APIs (Cohere AI, Pexels, Supabase) 
with rate limits that vary by service tier. The system must:
- Operate within current tier limits (free tier minimums)
- Gracefully handle rate limit errors
- Support upgrade path to paid tiers for increased capacity
- Implement fallback mechanisms when limits are reached
```

