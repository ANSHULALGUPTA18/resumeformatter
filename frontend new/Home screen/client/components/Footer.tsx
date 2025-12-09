export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full bg-white border-t border-gray-200/80 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div className="flex items-center justify-center">
          <p className="text-sm sm:text-base text-gray-700 font-roboto font-semibold text-center">
            © {currentYear} Resume Formatter Pro • Powered by TECHGENE
          </p>
        </div>
      </div>
    </footer>
  );
}
