import { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { CarCard, Car } from '@/components/CarCard';
import { FilterDropdown, Filters } from '@/components/FilterDropdown';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Search, Send, Sparkles, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase, isSupabaseReady } from '@/integrations/supabase/client';
import { useToast } from '@/hooks/use-toast';
import { searchCars, searchCarsWithFilters } from '@/services/api';

const initialFilters: Filters = {
  bodyTypes: [],
  makes: '',
  models: '',
  minYear: '',
  maxYear: '',
  minPrice: '',
  maxPrice: '',
  colors: [],
  maxMileage: '',
};

const Results = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState<Filters>(initialFilters);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [cars, setCars] = useState<Car[]>([]);
  const [lastId, setLastId] = useState<string | number | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  // Load filters from URL params
  useEffect(() => {
    const bodyTypes = searchParams.get('bodyTypes')?.split(',').filter(Boolean) || [];
    const colors = searchParams.get('colors')?.split(',').filter(Boolean) || [];
    
    setFilters({
      bodyTypes,
      makes: searchParams.get('makes')?.split(',').filter(Boolean).join(',') || '',
      models: '',
      colors,
      minYear: searchParams.get('minYear') || '',
      maxYear: searchParams.get('maxYear') || '',
      minPrice: searchParams.get('minPrice') || '',
      maxPrice: searchParams.get('maxPrice') || '',
      maxMileage: searchParams.get('maxMileage') || '',
    });
  }, [searchParams]);

  // Fetch cars when component mounts or params change
  useEffect(() => {
    const fetchCars = async () => {
      if (isInitialLoad) {
        setIsInitialLoad(false);
        await performSearch();
      }
    };
    fetchCars();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const performSearch = async (loadMore: boolean = false) => {
    if (loadMore) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
      setCars([]); // Clear existing results on new search
      setLastId(null); // Reset cursor
    }

    try {
      let response;
      
      // Check if we have active filters
      const hasFilters = 
        filters.bodyTypes.length > 0 ||
        filters.colors.length > 0 ||
        filters.minYear ||
        filters.maxYear ||
        filters.minPrice ||
        filters.maxPrice ||
        filters.maxMileage;

      // Use last_id for pagination if loading more
      const cursorId = loadMore ? lastId : null;

      if (hasFilters || !query.trim()) {
        // Use filtered search
        response = await searchCarsWithFilters(filters, query.trim() || undefined, cursorId);
      } else {
        // Use AI search
        response = await searchCars(query.trim(), filters, cursorId);
      }

      if (loadMore) {
        // Append new results to existing ones
        setCars(prev => [...prev, ...response.cars]);
      } else {
        // Replace results with new search
        setCars(response.cars);
      }

      // Update cursor for next page
      setLastId(response.last_id || null);
      // Check if there are more results (if we got 10 results, there might be more)
      setHasMore(response.cars.length === 10 && response.last_id !== null);
      
      if (!loadMore && response.cars.length === 0) {
        toast({
          title: "No results found",
          description: "Try adjusting your search criteria or filters.",
          variant: "default",
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      if (!loadMore) {
        toast({
          title: "Search failed",
          description: error instanceof Error ? error.message : "Could not fetch car listings. Please check if the backend is running.",
          variant: "destructive",
        });
        setCars([]);
      } else {
        toast({
          title: "Failed to load more",
          description: error instanceof Error ? error.message : "Could not load more results.",
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  const handleLoadMore = async () => {
    if (!isLoadingMore && hasMore) {
      await performSearch(true);
    }
  };

  const hasActiveFilters = 
    filters.bodyTypes.length > 0 ||
    (filters.makes && filters.makes.trim()) ||
    (filters.models && filters.models.trim()) ||
    filters.colors.length > 0 ||
    filters.minYear ||
    filters.maxYear ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.maxMileage;

  const handleSearch = async () => {
    if (!query.trim() && !hasActiveFilters) {
      toast({
        title: "Please enter a description or select filters",
        description: "Tell us what kind of car you're looking for or use the filter options.",
        variant: "destructive",
      });
      return;
    }

    // Save to search history if logged in and Supabase is configured
    if (user && isSupabaseReady) {
      try {
        await supabase.from('search_history').insert([{
          user_id: user.id,
          query: query.trim() || 'Filter search',
          filters: JSON.parse(JSON.stringify(filters)),
        }]);
      } catch (err) {
        // Silently fail if database isn't set up yet
        console.log('Search history not available yet');
      }
    }

    // Update URL params
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (filters.bodyTypes.length > 0) params.set('bodyTypes', filters.bodyTypes.join(','));
    if (filters.minYear) params.set('minYear', filters.minYear);
    if (filters.maxYear) params.set('maxYear', filters.maxYear);
    if (filters.minPrice) params.set('minPrice', filters.minPrice);
    if (filters.maxPrice) params.set('maxPrice', filters.maxPrice);
    if (filters.colors.length > 0) params.set('colors', filters.colors.join(','));
    if (filters.maxMileage) params.set('maxMileage', filters.maxMileage);

    navigate(`/results?${params.toString()}`);
    
    // Perform the search
    await performSearch();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };


  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        {/* Search Chat */}
        <div className="mb-8">
          <div className="relative bg-card rounded-2xl shadow-elevated p-2">
            <div className="flex items-start gap-2">
              <Textarea
                placeholder="Describe your perfect car... e.g., 'I need a reliable family SUV under $35,000 with good fuel economy'"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                className="min-h-[80px] resize-none border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base"
              />
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-border/50">
              <div className="flex items-center gap-3">
                <FilterDropdown
                  filters={filters}
                  onFiltersChange={setFilters}
                  onClearFilters={() => setFilters(initialFilters)}
                />
                <div className="hidden sm:flex items-center gap-2 text-muted-foreground text-sm">
                  <Sparkles className="h-4 w-4 text-secondary" />
                  <span>AI-powered</span>
                </div>
              </div>
              <Button 
                variant="hero" 
                size="lg" 
                onClick={handleSearch}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>Finding cars...</>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Results Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Search className="h-4 w-4" />
            {initialQuery && <p className="text-sm">"{initialQuery}"</p>}
            {initialQuery && <span className="text-border">•</span>}
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <p className="text-sm">Searching...</p>
              </div>
            ) : (
              <p className="text-sm">{cars.length} {cars.length === 1 ? 'car' : 'cars'} found{hasMore && ' (more available)'}</p>
            )}
          </div>
        </div>

        {/* Results Grid */}
        {isLoading ? (
          <div className="text-center py-16">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Searching for cars...</p>
          </div>
        ) : cars.length > 0 ? (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cars.map((car, index) => (
                <CarCard key={car.id} car={car} index={index} />
              ))}
            </div>
            {/* Load More Button */}
            {hasMore && (
              <div className="mt-8 text-center">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={handleLoadMore}
                  disabled={isLoadingMore}
                  className="min-w-[200px]"
                >
                  {isLoadingMore ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Loading more...
                    </>
                  ) : (
                    <>
                      Load More Cars
                    </>
                  )}
                </Button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-16">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <h2 className="font-display text-xl font-semibold text-foreground mb-2">
              No cars found
            </h2>
            <p className="text-muted-foreground mb-6">
              Try adjusting your filters or search with different criteria.
            </p>
            <Button variant="outline" onClick={() => {
              setFilters(initialFilters);
              navigate('/results');
            }}>
              Clear All Filters
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;
