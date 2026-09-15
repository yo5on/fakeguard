import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Account } from '../types';
import RiskBadge from '../components/RiskBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';
import './Accounts.css';

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState('');

  const loadAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getAccounts({
        skip: page * limit,
        limit,
        search: search || undefined,
        category: category || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setAccounts(response.accounts);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, [page, search, category, sortBy, sortOrder]);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
    setPage(0);
  };

  const handleImport = async () => {
    if (!csvFile) return;

    try {
      setImporting(true);
      setImportMessage('');
      const result = await api.importCSV(csvFile);
      setImportMessage(
        `Imported: ${result.imported}, Skipped: ${result.skipped}${
          result.errors.length > 0 ? `, Errors: ${result.errors.length}` : ''
        }`
      );
      setCsvFile(null);
      loadAccounts();
    } catch (err) {
      setImportMessage(`Import failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setImporting(false);
    }
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && accounts.length === 0) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadAccounts} />;

  return (
    <div className="accounts">
      <div className="container">
        <h1>Accounts</h1>

        <div className="accounts-controls card">
          <div className="controls-row">
            <input
              type="text"
              placeholder="Search by username..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
              className="search-input"
            />

            <select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setPage(0);
              }}
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
              type="file"
              accept=".csv"
              onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
              id="csv-upload"
              style={{ display: 'none' }}
            />
            <label htmlFor="csv-upload" className="btn btn-secondary">
              Choose CSV File
            </label>
            {csvFile && <span className="file-name">{csvFile.name}</span>}
            {csvFile && (
              <button
                onClick={handleImport}
                disabled={importing}
                className="btn btn-primary"
              >
                {importing ? 'Importing...' : 'Import'}
              </button>
            )}
          </div>
          {importMessage && (
            <div className="import-message">{importMessage}</div>
          )}
        </div>

        {accounts.length === 0 ? (
          <EmptyState message="No accounts found" />
        ) : (
          <>
            <div className="card">
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th onClick={() => handleSort('username')} className="sortable">
                        Username {sortBy === 'username' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                      <th onClick={() => handleSort('age_days')} className="sortable">
                        Age (days) {sortBy === 'age_days' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                      <th onClick={() => handleSort('followers')} className="sortable">
                        Followers {sortBy === 'followers' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                      <th onClick={() => handleSort('following')} className="sortable">
                        Following {sortBy === 'following' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                      <th>Risk Score</th>
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
                          <Link to={`/accounts/${account.id}`} className="btn-link">
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pagination">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="btn btn-secondary"
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {page + 1} of {totalPages} ({total} total)
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="btn btn-secondary"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}