import React, { useState, useEffect } from 'react';
import { semanticSearch } from '../../lib/services/semanticSearch';
import styles from './SemanticSearchModal.module.scss';

interface SearchResult {
  provider: string;
  services: string;
}

interface SemanticSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SemanticSearchModal: React.FC<SemanticSearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (results.length > 0) {
      const modalElement = document.querySelector(`.${styles.results}`);
      if (modalElement) {
        modalElement.scrollTo({ top: 0, behavior: "auto"});
      }
    }
  }, [results]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await semanticSearch(query);
      setResults(response.results);
    } catch (err) {
      setError('Failed to perform search. Please try again.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getProviderInfo = (provider: string) => {
    const firstParenIndex = provider.indexOf('(');
    const lastParenIndex = provider.lastIndexOf('(');
    console.log(">>>", provider)
    const name = firstParenIndex !== -1
      ? provider.slice(0, firstParenIndex).trim()
      : provider;

    const address = lastParenIndex !== -1
      ? provider.slice(lastParenIndex + 1, provider.lastIndexOf(')')).trim()
      : null;

    return { name, address };
  };

  if (!isOpen) return null;

  return (
    <div className={`${styles.modalOverlay} ${results.length > 0 ? styles.hasResults : ''}`} onClick={(e) => e.stopPropagation()}>
      <div className={styles.modal}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close modal">
          <svg 
            className={styles.closeIcon}
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path 
              d="M6 18L18 6M6 6L18 18" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <h2 className={styles.title}>Resource Lookup</h2>

        <form onSubmit={handleSearch} className={styles.searchForm}>
          <div className={styles.searchInputWrapper}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search services..."
              className={styles.searchInput}
            />
            <button type="submit" className={styles.searchButton} disabled={isLoading}>
              <svg 
                className={styles.searchIcon}
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path 
                  d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
            {isLoading && <span className={styles.loading}>Searching...</span>}
            {error && <span className={styles.error}>{error}</span>}
          </div>
        </form>

        {results.length > 0 && (
          <div className={styles.results}>
            {results.map((result, index) => {
              const { name, address } = getProviderInfo(result.provider);
              return (
                <div key={index} className={styles.resultItem}>
                  <a 
                    href={`/listings?search=${encodeURIComponent(name)}`}
                    className={styles.providerLink}
                  >
                    {name}
                  </a>
                  {address && (
                    <div className={styles.address}>{address}</div>
                  )}
                  <p className={styles.services}>{result.services}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SemanticSearchModal;