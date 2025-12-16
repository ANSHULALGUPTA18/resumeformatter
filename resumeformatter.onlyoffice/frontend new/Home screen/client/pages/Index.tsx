import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { TemplateSection } from "@/components/TemplateSection";
import { useState } from "react";

const SAMPLE_TEMPLATES = [
  { id: "1", name: "def", fileType: "DOCX", isFavorite: false },
  { id: "2", name: "Abc", fileType: "DOCX", isFavorite: true },
  { id: "3", name: "def", fileType: "DOCX", isFavorite: false },
  { id: "4", name: "Abc", fileType: "DOCX", isFavorite: true },
  { id: "5", name: "def", fileType: "DOCX", isFavorite: false },
  { id: "6", name: "Abc", fileType: "DOCX", isFavorite: true },
  { id: "7", name: "Abc", fileType: "DOCX", isFavorite: true },
];

export default function Index() {
  const [allTemplates, setAllTemplates] = useState(SAMPLE_TEMPLATES);
  const [favorites, setFavorites] = useState(
    new Set(SAMPLE_TEMPLATES.filter((t) => t.isFavorite).map((t) => t.id)),
  );

  const handleToggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(id)) {
      newFavorites.delete(id);
    } else {
      newFavorites.add(id);
    }
    setFavorites(newFavorites);
  };

  const handleTemplateSelect = (id: string) => {
    console.log("Selected template:", id);
  };

  const favoriteTemplates = allTemplates.filter((t) => favorites.has(t.id));

  return (
    <div className="flex flex-col min-h-screen bg-secondary">
      <Header />

      <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="space-y-3">
          {/* Choose Your Template Section */}
          <TemplateSection
            title="Choose Your Template"
            templates={allTemplates}
            showSearch={true}
            onTemplateSelect={handleTemplateSelect}
            onToggleFavorite={handleToggleFavorite}
          />

          {/* Favorite Section */}
          {favoriteTemplates.length > 0 && (
            <TemplateSection
              title="Favorite"
              templates={favoriteTemplates}
              showSearch={false}
              onTemplateSelect={handleTemplateSelect}
              onToggleFavorite={handleToggleFavorite}
            />
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
