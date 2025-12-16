import { useState, useRef } from "react";
import { Search } from "lucide-react";
import { TemplateCard } from "./TemplateCard";

interface Template {
  id: string;
  name: string;
  fileType: string;
  isFavorite?: boolean;
}

interface TemplateSectionProps {
  title?: string;
  templates: Template[];
  showSearch?: boolean;
  onTemplateSelect?: (id: string) => void;
  onToggleFavorite?: (id: string) => void;
}

export function TemplateSection({
  title,
  templates,
  showSearch = false,
  onTemplateSelect,
  onToggleFavorite,
}: TemplateSectionProps) {
  const [favorites, setFavorites] = useState<Set<string>>(
    new Set(templates.filter((t) => t.isFavorite).map((t) => t.id)),
  );
  const [searchQuery, setSearchQuery] = useState("");
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const handleToggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(id)) {
      newFavorites.delete(id);
    } else {
      newFavorites.add(id);
    }
    setFavorites(newFavorites);
    onToggleFavorite?.(id);
  };

  const scroll = (direction: "left" | "right") => {
    if (scrollContainerRef.current) {
      const scrollAmount = 150;
      scrollContainerRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  const filteredTemplates = templates.filter((template) =>
    template.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="w-full">
      {/* Search Bar - Only for "Choose Your Template" section */}
      {showSearch && (
        <div className="mb-3 flex flex-col items-center w-full">
          <h2 className="text-xl font-outfit font-bold text-primary mb-2.5 text-center">
            {title}
          </h2>
          <div className="flex items-center gap-3 bg-white rounded-2xl border border-gray-500 px-4 py-2 w-full max-w-3xl">
            <Search className="w-4 h-4 text-gray-600 flex-shrink-0" />
            <input
              type="text"
              placeholder="Search templates by name"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-500 outline-none"
            />
          </div>
        </div>
      )}

      {/* Dark Container with Title (for Favorite) and Carousel */}
      <div className="relative bg-gray-600 rounded-lg p-4 flex flex-col">
        {/* Title inside container for non-search sections */}
        {!showSearch && title && (
          <h2 className="text-lg font-outfit font-bold text-white mb-3 text-center">
            {title}
          </h2>
        )}

        {/* Carousel Container */}
        <div className="flex items-center">
          <button
            onClick={() => scroll("left")}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-10 p-2 bg-gray-700 hover:bg-gray-800 text-white rounded-full transition-colors"
            aria-label="Scroll left"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </button>

          <div
            ref={scrollContainerRef}
            className="flex gap-3 overflow-x-auto scroll-smooth scrollbar-hide mx-10 flex-1"
          >
            {filteredTemplates.length > 0 ? (
              filteredTemplates.map((template) => (
                <div key={template.id} className="flex-shrink-0">
                  <TemplateCard
                    id={template.id}
                    name={template.name}
                    fileType={template.fileType}
                    isFavorite={favorites.has(template.id)}
                    onFavorite={handleToggleFavorite}
                    onSelect={onTemplateSelect}
                  />
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center w-full h-28 text-gray-400 text-sm">
                No templates found
              </div>
            )}

            {showSearch && (
              <div className="flex-shrink-0 flex flex-col items-center justify-center w-20 h-28 border-2 border-dashed border-white rounded-xl bg-transparent text-white">
                <div className="text-3xl mb-1">+</div>
                <div className="text-xs text-center px-1">Add New Template</div>
              </div>
            )}
          </div>

          <button
            onClick={() => scroll("right")}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-10 p-2 bg-gray-700 hover:bg-gray-800 text-white rounded-full transition-colors"
            aria-label="Scroll right"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
