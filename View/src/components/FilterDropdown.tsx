import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SlidersHorizontal, X, Check } from 'lucide-react';
import { cn } from '@/lib/util';

export interface Filters {
  bodyTypes: string[];
  makes: string;
  models: string;
  minYear: string;
  maxYear: string;
  minPrice: string;
  maxPrice: string;
  colors: string[];
  maxMileage: string;
}

interface FilterDropdownProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  onClearFilters: () => void;
}

const BODY_TYPES = ['SUV', 'Sedan', 'Truck', 'Coupe', 'Hatchback', 'Convertible', 'Van', 'Hybrid'];
const COLORS = ['Black', 'White', 'Silver', 'Gray', 'Red', 'Blue', 'Green', 'Brown', 'Yellow', 'Orange', 'Purple', 'Pink', 'Beige', 'Gold', 'Tan', 'Maroon', 'Navy', 'Teal'];

// Unique makes from database (sorted alphabetically)
const MAKES = [
  'Acura', 'Alfa', 'Aston', 'Audi', 'Austin', 'Bentley', 'BMW', 'Buick', 'Cadillac', 'Chevrolet',
  'Chrysler', 'Datsun', 'De', 'Dodge', 'Ferrari', 'Fiat', 'Ford', 'Freightliner', 'Genesis', 'GMC',
  'Hino', 'Honda', 'Hummer', 'Hyundai', 'Infiniti', 'International', 'Jaguar', 'Jeep', 'JLG', 'Kia',
  'Lamborghini', 'Land', 'Lexus', 'Lincoln', 'Lotus', 'Maserati', 'Matrix', 'Mazda', 'McLaren', 'Mercedes',
  'Mercedes-Benz', 'Mercury', 'MG', 'MINI', 'Mitsubishi', 'Morgan', 'Nissan', 'Oldsmobile', 'Plymouth',
  'Polaris', 'Polestar', 'Pontiac', 'Porsche', 'RAM', 'Rivian', 'Rolls', 'Saturn', 'Scion', 'SEASWIRL',
  'Smart', 'Subaru', 'Suzuki', 'Tesla', 'Toyota', 'Vespa', 'VinFast', 'Volkswagen', 'VOLKSWAON', 'Volvo', 'Workhorse'
].sort();

export function FilterDropdown({ filters, onFiltersChange, onClearFilters }: FilterDropdownProps) {
  const [makeSearch, setMakeSearch] = useState('');
  const [makeOpen, setMakeOpen] = useState(false);
  const makeDropdownRef = useRef<HTMLDivElement>(null);
  
  // Filter makes based on search
  const filteredMakes = MAKES.filter(make => 
    make.toLowerCase().includes(makeSearch.toLowerCase())
  );
  
  // Close make dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (makeDropdownRef.current && !makeDropdownRef.current.contains(event.target as Node)) {
        setMakeOpen(false);
      }
    };
    
    if (makeOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [makeOpen]);
  
  const hasActiveFilters = 
    filters.bodyTypes.length > 0 ||
    filters.makes ||
    filters.models ||
    filters.colors.length > 0 ||
    filters.minYear ||
    filters.maxYear ||
    filters.minPrice ||
    filters.maxPrice ||
    filters.maxMileage;

  // For body type: single selection only
  const toggleSingleFilter = (key: 'bodyTypes', value: string) => {
    const current = filters[key];
    const updated = current.includes(value) ? [] : [value];
    onFiltersChange({ ...filters, [key]: updated });
  };

  // For colors: multiple selection allowed
  const toggleArrayFilter = (key: 'colors', value: string) => {
    const current = filters[key];
    const updated = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    onFiltersChange({ ...filters, [key]: updated });
  };

  return (
    <div className="flex items-center gap-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="gap-2">
            <SlidersHorizontal className="h-4 w-4" />
            Filters
            {hasActiveFilters && (
              <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-secondary text-xs text-secondary-foreground">
                !
              </span>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-80 p-4 bg-popover max-h-[70vh] overflow-y-auto" align="start">
          <DropdownMenuLabel className="text-base font-semibold">Advanced Filters</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {/* Make - Searchable dropdown */}
          <div className="py-2">
            <Label className="text-sm font-medium">Make</Label>
            <div className="mt-2 space-y-2 relative" ref={makeDropdownRef}>
              <Input
                placeholder="Search makes..."
                value={makeSearch}
                onChange={(e) => {
                  setMakeSearch(e.target.value);
                  setMakeOpen(true);
                }}
                className="h-9"
                onFocus={() => setMakeOpen(true)}
              />
              {makeOpen && (
                <div className="absolute z-50 w-full mt-1 border rounded-md bg-popover shadow-md max-h-[200px] overflow-y-auto">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-left font-normal h-9"
                    onClick={() => {
                      onFiltersChange({ ...filters, makes: '' });
                      setMakeSearch('');
                      setMakeOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        filters.makes === '' ? "opacity-100" : "opacity-0"
                      )}
                    />
                    All Makes
                  </Button>
                  {filteredMakes.map((make) => (
                    <Button
                      key={make}
                      variant="ghost"
                      className="w-full justify-start text-left font-normal h-9"
                      onClick={() => {
                        onFiltersChange({ ...filters, makes: make });
                        setMakeSearch('');
                        setMakeOpen(false);
                      }}
                    >
                      <Check
                        className={cn(
                          "mr-2 h-4 w-4",
                          filters.makes === make ? "opacity-100" : "opacity-0"
                        )}
                      />
                      {make}
                    </Button>
                  ))}
                  {filteredMakes.length === 0 && (
                    <div className="p-2 text-sm text-muted-foreground text-center">No make found</div>
                  )}
                </div>
              )}
              {filters.makes && !makeOpen && (
                <div className="text-sm text-muted-foreground">Selected: {filters.makes}</div>
              )}
            </div>
          </div>

          <DropdownMenuSeparator />

          {/* Model - Text input */}
          <div className="py-2">
            <Label className="text-sm font-medium">Model</Label>
            <Input
              placeholder="Enter model name"
              value={filters.models || ''}
              onChange={(e) => onFiltersChange({ ...filters, models: e.target.value })}
              className="h-9 mt-2"
            />
          </div>

          <DropdownMenuSeparator />
          
          {/* Body Type - Single selection */}
          <div className="py-2">
            <Label className="text-sm font-medium">Body Type (select one)</Label>
            <div className="flex flex-wrap gap-1 mt-2">
              {BODY_TYPES.map(type => (
                <Button
                  key={type}
                  variant={filters.bodyTypes.includes(type) ? 'secondary' : 'outline'}
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => toggleSingleFilter('bodyTypes', type)}
                >
                  {type}
                </Button>
              ))}
            </div>
          </div>

          <DropdownMenuSeparator />

          {/* Year Range */}
          <div className="py-2">
            <Label className="text-sm font-medium">Year Range</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <Input
                placeholder="Min Year"
                type="number"
                value={filters.minYear}
                onChange={(e) => onFiltersChange({ ...filters, minYear: e.target.value })}
                className="h-9"
              />
              <Input
                placeholder="Max Year"
                type="number"
                value={filters.maxYear}
                onChange={(e) => onFiltersChange({ ...filters, maxYear: e.target.value })}
                className="h-9"
              />
            </div>
          </div>

          <DropdownMenuSeparator />

          {/* Price Range */}
          <div className="py-2">
            <Label className="text-sm font-medium">Price Range</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <Input
                placeholder="Min Price"
                type="number"
                value={filters.minPrice}
                onChange={(e) => onFiltersChange({ ...filters, minPrice: e.target.value })}
                className="h-9"
              />
              <Input
                placeholder="Max Price"
                type="number"
                value={filters.maxPrice}
                onChange={(e) => onFiltersChange({ ...filters, maxPrice: e.target.value })}
                className="h-9"
              />
            </div>
          </div>

          <DropdownMenuSeparator />

          {/* Colors */}
          <div className="py-2">
            <Label className="text-sm font-medium">Color</Label>
            <div className="flex flex-wrap gap-1 mt-2">
              {COLORS.map(color => (
                <Button
                  key={color}
                  variant={filters.colors.includes(color) ? 'secondary' : 'outline'}
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => toggleArrayFilter('colors', color)}
                >
                  {color}
                </Button>
              ))}
            </div>
          </div>

          <DropdownMenuSeparator />

          {/* Mileage */}
          <div className="py-2">
            <Label className="text-sm font-medium">Max Mileage</Label>
            <Input
              placeholder="e.g., 50000"
              type="number"
              value={filters.maxMileage}
              onChange={(e) => onFiltersChange({ ...filters, maxMileage: e.target.value })}
              className="h-9 mt-2"
            />
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={onClearFilters} className="gap-1.5">
          <X className="h-4 w-4" />
          Clear
        </Button>
      )}
    </div>
  );
}
