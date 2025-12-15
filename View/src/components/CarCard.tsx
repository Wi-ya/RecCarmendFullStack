import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Gauge, Calendar } from 'lucide-react';

export interface Car {
  id: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  bodyType: string;
  color: string;
  image: string;
  location: string;
  url?: string;
  colorHex?: string | null; // Hex color code for color indicator
}

interface CarCardProps {
  car: Car;
  index: number;
}

// Helper function to get color hex code from color name
function getColorHex(colorName: string | null | undefined): string | null {
  if (!colorName) return null;
  
  const colorMap: Record<string, string> = {
    'black': '#000000',
    'white': '#FFFFFF',
    'red': '#FF0000',
    'blue': '#0000FF',
    'green': '#008000',
    'yellow': '#FFFF00',
    'orange': '#FFA500',
    'purple': '#800080',
    'pink': '#FFC0CB',
    'brown': '#A52A2A',
    'beige': '#F5F5DC',
    'gray': '#808080',
    'grey': '#808080',
    'silver': '#C0C0C0',
    'gold': '#FFD700',
    'tan': '#D2B48C',
    'burgundy': '#800020',
    'navy': '#000080',
    'teal': '#008080',
    'maroon': '#800000',
  };
  
  const colorLower = colorName.toLowerCase().trim();
  
  // Check for exact match first
  if (colorLower in colorMap) {
    return colorMap[colorLower];
  }
  
  // Check if color name contains any of the mapped colors
  for (const [mappedColor, hexCode] of Object.entries(colorMap)) {
    if (colorLower.includes(mappedColor)) {
      return hexCode;
    }
  }
  
  return null;
}

export function CarCard({ car, index }: CarCardProps) {
  const [imageError, setImageError] = useState(false);
  
  // Generate fallback image URL if image fails to load
  const getFallbackImage = () => {
    const searchQuery = `${car.year} ${car.make} ${car.model} car`.trim();
    if (searchQuery && searchQuery !== 'car') {
      return `https://source.unsplash.com/600x400/?${encodeURIComponent(searchQuery)}`;
    }
    // Generic car image fallback
    return 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&h=400&fit=crop&auto=format';
  };

  return (
    <Card 
      className="group overflow-hidden border-border/50 bg-card shadow-card hover:shadow-elevated transition-all duration-300 animate-slide-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="relative aspect-[16/10] overflow-hidden bg-muted">
        <img
          src={imageError ? getFallbackImage() : car.image}
          alt={`${car.year} ${car.make} ${car.model}`}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          onError={() => setImageError(true)}
        />
        <Badge className="absolute top-3 left-3 bg-secondary text-secondary-foreground">
          {car.bodyType}
        </Badge>
      </div>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="font-display text-xl font-semibold text-foreground">
              {car.year} {car.make} {car.model}
            </h3>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-foreground">
              ${car.price.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-border/50">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Gauge className="h-4 w-4" />
            <span>{car.mileage.toLocaleString()} mi</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{car.year}</span>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Badge variant="outline" className="text-xs flex items-center gap-2">
            {(car.colorHex || getColorHex(car.color)) && (
              <span 
                className="w-3.5 h-3.5 rounded-full border border-border/50 flex-shrink-0"
                style={{ backgroundColor: car.colorHex || getColorHex(car.color) || '#808080' }}
              />
            )}
            <span>{car.color}</span>
          </Badge>
          {car.url ? (
            <Button 
              variant="default" 
              size="sm"
              onClick={() => window.open(car.url, '_blank', 'noopener,noreferrer')}
            >
              View Details
            </Button>
          ) : (
            <Button variant="default" size="sm" disabled>
              View Details
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
