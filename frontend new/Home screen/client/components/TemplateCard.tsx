import { useState } from "react";

interface TemplateCardProps {
  id: string;
  name: string;
  fileType: string;
  isFavorite?: boolean;
  onFavorite?: (id: string) => void;
  onSelect?: (id: string) => void;
}

export function TemplateCard({
  id,
  name,
  fileType,
  isFavorite = false,
  onFavorite,
  onSelect,
}: TemplateCardProps) {
  const [hovering, setHovering] = useState(false);

  return (
    <div
      className="relative flex flex-col w-20 h-28 rounded-xl border border-gray-400 bg-white overflow-hidden shadow-sm transition-shadow hover:shadow-md cursor-pointer"
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      onClick={() => onSelect?.(id)}
    >
      {/* Star Button */}
      <button
        className="absolute top-0.5 right-0.5 z-10 p-0.5 hover:bg-gray-100 rounded-full transition-colors text-base"
        onClick={(e) => {
          e.stopPropagation();
          onFavorite?.(id);
        }}
        title={isFavorite ? "Remove from favorites" : "Add to favorites"}
      >
        {isFavorite ? "⭐" : "☆"}
      </button>

      {/* More Options Button */}
      <button
        className="absolute top-0.5 left-0.5 z-10 text-gray-500 hover:text-gray-700 text-xs font-bold"
        onClick={(e) => e.stopPropagation()}
        title="More options"
      >
        ⋮
      </button>

      {/* Preview Area */}
      <div className="flex flex-col items-center justify-center bg-gray-100 border-b border-gray-200 py-2 px-1.5 flex-1">
        <div className="flex flex-col items-center gap-1">
          <div className="text-xl opacity-60">📄</div>
          <div className="flex flex-col gap-0.5 w-12">
            <div className="h-0.5 bg-gray-300 rounded"></div>
            <div className="h-0.5 bg-gray-300 rounded"></div>
            <div className="h-0.5 bg-gray-300 rounded w-8"></div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex flex-col gap-0.5 p-1.5 text-center">
        <div className="flex items-center justify-center gap-0.5">
          <span className="text-xs">📄</span>
          <span className="text-xs text-gray-500">{fileType}</span>
        </div>
        <div className="font-roboto font-bold text-xs text-gray-900 leading-tight">
          {name}
        </div>
      </div>
    </div>
  );
}
