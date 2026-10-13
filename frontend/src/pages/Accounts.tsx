import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Account, AccountSortField, ImportResult } from '../types';
import RiskBadge from '../components/RiskBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import './Accounts.css';

const PAGE_SIZE = 20;
const MAX_IMPORT_ERRORS_SHOWN = 10;

const SORTABLE_COLUMNS: { field: AccountSortField; label: string }[] = [
  { field: 'username', label: 'Username' },
  { field: 'age_days', label: 'Age (days)' },
  { field: 'followers', label: 'Followers' },
  { field: 'following', label: 'Following' },
  { field: 'risk_score', label: 'Risk Score' },
];

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search.trim(), 300);
  const [category, setCategory] = useState('');
  const [sortBy, setSortBy] = useState<AccountSortField>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const reload = useCallback(() => setReloadToken((n) => n + 1), []);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    api
      .getAccounts(
        {
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE,
          search: debouncedSearch || undefined,
          category: category || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        },
        { signal: controller.signal },
      )
      .then((response) => {
        setAccounts(response.accounts);
        setTotal(response.total);
        setLoading(false);
      })
      .catch((err) => {
        // A newer request superseded this one; ignore its outcome.
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err.message : 'Failed to load accounts');
        setLoading(false);
      });

    return () => controller.abort();
  }, [page, debouncedSearch, category, sortBy, sortOrder, reloadToken]);

  // Return to the first page whenever the result set changes shape.
  useEffect(() => {
    setPage(0);
  }, [debouncedSearch, category]);

  const handleSort = (field: AccountSortField) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder(field === 'risk_score' ? 'desc' : 'asc');
    }
    setPage(0);
  };

  const handleImport = async () => {
    if (!csvFile) return;

    try {
      setImporting(true);
      setImportResult(null);
      setImportError(null);
      const result = await api.importCSV(csvFile);
      setImportResult(result);
      setCsvFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      reload();
    } catch (err) {
      setImportError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setImporting(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const initialLoad = loading && accounts.length === 0 && !error;

  return (
    <div className="accounts">
      <div className="container">
        <h1>Accounts</h1>

        <div className="accounts-controls card">
          <div className="controls-row">
            <input
              type="search"
              placeholder="Search by username..."
              aria-label="Search accounts by username"
              value={search}
              maxLength={255}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />

            <select
              value={category}
              aria-label="Filter by risk category"
              onChange={(e) => setCategory(e.target.value)}
              className="filter-select"
            >
              <option value="">All Categories</option>
              <option value="LOW">Low Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="CRITICAL">Critical Risk</option>
            </select>
          </div>

          <div className="import-section">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => {
                setCsvFile(e.target.files?.[0] || null);
                setImportResult(null);
                setImportError(null);
              }}
              id="csv-upload"
              className="visually-hidden"
            />
            <label htmlFor="csv-upload" className="btn btn-secondary">
              Choose CSV File
            </label>
            {csvFile && <span className="file-name">{csvFile.name}</span>}
            {csvFile && (
              <button
                type="button"
                onClick={handleImport}
                disabled={importing}
                className="btn btn-primary"
              >
                {importing ? 'Importing...' : 'Import'}
              </button>
            )}
          </div>
          <div aria-live="polite">
            {importResult && (
              <div className="import-message">
                Imported: {importResult.imported}, Skipped: {importResult.skipped}
                {importResult.errors.length > 0 && `, Errors: ${importResult.errors.length}`}
                {importResult.errors.length > 0 && (
                  <ul className="import-errors">
                    {importResult.errors.slice(0, MAX_IMPORT_ERRORS_SHOWN).map((message) => (
                      <li key={message}>{message}</li>
                    ))}
                    {importResult.errors.length > MAX_IMPORT_ERRORS_SHOWN && (
                      <li>…and {importResult.errors.length - MAX_IMPORT_ERRORS_SHOWN} more</li>
                    )}
                  </ul>
                )}
              </div>
            )}
            {importError && (
              <div className="import-message import-message-error" role="alert">
                Import failed: {importError}
              </div>
            )}
          </div>
        </div>

        {initialLoad ? (
          <LoadingState />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : accounts.length === 0 ? (
          <EmptyState message="No accounts found" />
        ) : (
          <>
            <div className="card" aria-busy={loading}>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      {SORTABLE_COLUMNS.map(({ field, label }) => {
                        const active = sortBy === field;
                        return (
                          <th
                            key={field}
                            aria-sort={active ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                          >
                            <button
                              type="button"
                              className="sort-button"
                              onClick={() => handleSort(field)}
                            >
                              {label}
                              <span aria-hidden="true">
                                {active ? (sortOrder === 'asc' ? ' ↑' : ' ↓') : ''}
                              </span>
                            </button>
                          </th>
                        );
                      })}
                      <th>Category</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.map((account) => (
                      <tr key={account.id}>
                        <td>{account.username}</td>
                        <td>{account.age_days}</td>
                        <td>{account.followers.toLocaleString()}</td>
                        <td>{account.following.toLocaleString()}</td>
                        <td>
                          {account.latest_analysis
                            ? Math.round(account.latest_analysis.risk_score)
                            : 'N/A'}
                        </td>
                        <td>
                          {account.latest_analysis ? (
                            <RiskBadge category={account.latest_analysis.category} size="sm" />
                          ) : (
                            'Not analyzed'
                          )}
                        </td>
                        <td>
                          <Link
                            to={`/accounts/${account.id}`}
                            className="btn-link"
                            aria-label={`View ${account.username}`}
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <nav className="pagination" aria-label="Accounts pagination">
              <button
                type="button"
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0 || loading}
                className="btn btn-secondary"
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {page + 1} of {totalPages} ({total} total)
              </span>
              <button
                type="button"
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1 || loading}
                className="btn btn-secondary"
              >
                Next
              </button>
            </nav>
          </>
        )}
      </div>
    </div>
  );
}
