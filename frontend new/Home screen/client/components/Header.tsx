export function Header() {
  return (
    <header className="w-full bg-white border-b border-gray-200/80 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-primary flex items-center justify-center text-white font-bold text-lg sm:text-xl shadow-lg">
              R
            </div>
            <div>
              <h1 className="text-xl sm:text-3xl font-roboto font-bold text-primary">
                Resume Formatter Pro
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 font-roboto font-light tracking-widest">
                powered by Techgene
              </p>
            </div>
          </div>
          <button className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-primary text-white shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center flex-shrink-0">
            <svg
              className="w-7 h-7 sm:w-8 sm:h-8"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M11.999 2C6.477 2 2 6.477 2 12s4.477 10 9.999 10C17.523 22 22 17.523 22 12S17.523 2 11.999 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
