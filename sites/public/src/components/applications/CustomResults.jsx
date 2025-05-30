import { useEffect, useState } from 'react';

function CustomResults({ customResults, loading }) {
  const [hasSearched, setHasSearched] = useState(false);
  const results = customResults?.results || [];

  useEffect(() => {
    if (!loading && customResults) {
      setHasSearched(true);
    }
  }, [loading, customResults]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-10">
        <svg
          className="animate-spin h-6 w-6 text-purple-600"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"
          />
        </svg>
        <span className="ml-3 text-purple-600">Loading results...</span>
      </div>
    );
  }

  if (hasSearched && results.length === 0) {
    return (
      <div className="text-center text-gray-500 py-10">
        No results found.
      </div>
    );
  }

  if (results.length === 0) {
    return null; 
  }

  return (
    <div className="space-y-4 py-6">
      {results.map((result, index) => {
          const firstParenIndex = result.provider.indexOf('(');
          const lastParenIndex = result.provider.lastIndexOf('(');

          const name =
            firstParenIndex !== -1
              ? result.provider.slice(0, firstParenIndex).trim()
              : result.provider;

          const address =
            lastParenIndex !== -1
              ? result.provider.slice(lastParenIndex + 1, result.provider.lastIndexOf(')')).trim()
              : null;


        return (
          <div
            key={index}
            className="bg-white shadow-md rounded-xl p-4 border border-gray-200 hover:shadow-lg transition-shadow"
          >
            <a
              href="#"
              className=" font-semibold text-blue-600 hover:text-blue-800 underline"
            >
              {name}
            </a>
            {address && (
              <div className="text-sm text-gray-600 mt-1">{address}</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default CustomResults;
