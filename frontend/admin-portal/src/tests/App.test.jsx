import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import { AdminProvider } from '../src/contexts/AdminContext';
import App from '../src/App';
import LoginPage from '../src/pages/LoginPage';
import DashboardPage from '../src/pages/DashboardPage';
import UsersPage from '../src/pages/UsersPage';
import SubscriptionsPage from '../src/pages/SubscriptionsPage';
import AuditLogsPage from '../src/pages/AuditLogsPage';
import ReportsPage from '../src/pages/ReportsPage';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock React Router
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
}));

// Mock Chart.js components
jest.mock('recharts', () => ({
  LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      <AdminProvider>
        {children}
      </AdminProvider>
    </AuthProvider>
  </BrowserRouter>
);

describe('Admin App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders login page by default', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    expect(screen.getByText(/Admin Portal/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign in to your admin account/i)).toBeInTheDocument();
  });
});

describe('Admin LoginPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders admin login form', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByText(/Admin Portal/i)).toBeInTheDocument();
  });

  test('handles admin login submission', async () => {
    const mockResponse = {
      access_token: 'admin-token',
      user: { 
        id: '1', 
        email: 'admin@subscriptionpro.com', 
        first_name: 'Admin',
        user_role: 'admin'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Sign In/i });

    fireEvent.change(emailInput, { target: { value: 'admin@subscriptionpro.com' } });
    fireEvent.change(passwordInput, { target: { value: 'admin123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'admin@subscriptionpro.com',
          password: 'admin123'
        })
      });
    });
  });

  test('displays error for non-admin users', async () => {
    const mockResponse = {
      access_token: 'user-token',
      user: { 
        id: '1', 
        email: 'user@example.com', 
        first_name: 'User',
        user_role: 'user'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Sign In/i });

    fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Access denied. Admin privileges required./i)).toBeInTheDocument();
    });
  });
});

describe('Admin DashboardPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('renders dashboard with statistics', async () => {
    const mockStats = {
      total_users: 150,
      active_subscriptions: 89,
      monthly_revenue: 125000,
      churn_rate: 5.2,
      growth_rate: 12.5
    };

    const mockRevenueData = [
      { month: 'Jan', revenue: 100000 },
      { month: 'Feb', revenue: 125000 }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockRevenueData,
      });

    render(
      <TestWrapper>
        <DashboardPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/150/)).toBeInTheDocument(); // Total users
      expect(screen.getByText(/89/)).toBeInTheDocument(); // Active subscriptions
      expect(screen.getByText(/₹1,25,000/)).toBeInTheDocument(); // Monthly revenue
      expect(screen.getByText(/5.2%/)).toBeInTheDocument(); // Churn rate
    });
  });

  test('renders charts', async () => {
    const mockStats = {
      total_users: 150,
      active_subscriptions: 89,
      monthly_revenue: 125000,
      churn_rate: 5.2
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockStats,
    });

    render(
      <TestWrapper>
        <DashboardPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });
});

describe('Admin UsersPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('renders users list', async () => {
    const mockUsers = [
      {
        user_id: '1',
        email: 'user1@example.com',
        first_name: 'John',
        last_name: 'Doe',
        user_role: 'user',
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        user_id: '2',
        email: 'user2@example.com',
        first_name: 'Jane',
        last_name: 'Smith',
        user_role: 'user',
        created_at: '2024-01-02T00:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ users: mockUsers, total: 2 }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
      expect(screen.getByText(/user1@example.com/i)).toBeInTheDocument();
      expect(screen.getByText(/user2@example.com/i)).toBeInTheDocument();
    });
  });

  test('handles user search', async () => {
    const mockUsers = [
      {
        user_id: '1',
        email: 'john@example.com',
        first_name: 'John',
        last_name: 'Doe',
        user_role: 'user',
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ users: mockUsers, total: 1 }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    const searchInput = screen.getByPlaceholderText(/Search users/i);
    fireEvent.change(searchInput, { target: { value: 'john' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/users?search=john&page=1&limit=20', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });

  test('handles role filter', async () => {
    const mockUsers = [];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ users: mockUsers, total: 0 }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    const roleSelect = screen.getByDisplayValue(/All Roles/i);
    fireEvent.change(roleSelect, { target: { value: 'admin' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/users?role=admin&page=1&limit=20', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });

  test('opens user details modal', async () => {
    const mockUsers = [
      {
        user_id: '1',
        email: 'user1@example.com',
        first_name: 'John',
        last_name: 'Doe',
        user_role: 'user',
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    const mockUserDetails = {
      ...mockUsers[0],
      phone_number: '+91-9876543210',
      address_line1: '123 Test Street',
      city: 'Mumbai',
      subscriptions: []
    };

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: mockUsers, total: 1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUserDetails,
      });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const viewButton = screen.getByText(/View/i);
      fireEvent.click(viewButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/User Details/i)).toBeInTheDocument();
      expect(screen.getByText(/+91-9876543210/i)).toBeInTheDocument();
    });
  });
});

describe('Admin SubscriptionsPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('renders subscriptions list', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        user: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        amount: 2999,
        next_delivery_date: '2024-02-01'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ subscriptions: mockSubscriptions, total: 1 }),
    });

    render(
      <TestWrapper>
        <SubscriptionsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      expect(screen.getByText(/Premium Coffee/i)).toBeInTheDocument();
      expect(screen.getByText(/Active/i)).toBeInTheDocument();
      expect(screen.getByText(/Monthly/i)).toBeInTheDocument();
    });
  });

  test('handles subscription modification', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        user: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        amount: 2999,
        next_delivery_date: '2024-02-01'
      }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ subscriptions: mockSubscriptions, total: 1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockSubscriptions[0], status: 'paused' }),
      });

    render(
      <TestWrapper>
        <SubscriptionsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const modifyButton = screen.getByText(/Modify/i);
      fireEvent.click(modifyButton);
    });

    // Change status to paused
    const statusSelect = screen.getByDisplayValue(/active/i);
    fireEvent.change(statusSelect, { target: { value: 'paused' } });

    const saveButton = screen.getByText(/Save Changes/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/subscriptions/1/modify', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer admin-token'
        },
        body: expect.stringContaining('"status":"paused"')
      });
    });
  });

  test('handles subscription extension', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        user: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        amount: 2999,
        next_delivery_date: '2024-02-01'
      }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ subscriptions: mockSubscriptions, total: 1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSubscriptions[0],
      });

    render(
      <TestWrapper>
        <SubscriptionsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const extendButton = screen.getByText(/Extend/i);
      fireEvent.click(extendButton);
    });

    const daysInput = screen.getByLabelText(/Days to extend/i);
    fireEvent.change(daysInput, { target: { value: '30' } });

    const confirmButton = screen.getByText(/Extend Subscription/i);
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/subscriptions/1/extend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer admin-token'
        },
        body: JSON.stringify({ days: 30 })
      });
    });
  });

  test('filters subscriptions by status', async () => {
    const mockSubscriptions = [];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ subscriptions: mockSubscriptions, total: 0 }),
    });

    render(
      <TestWrapper>
        <SubscriptionsPage />
      </TestWrapper>
    );

    const statusFilter = screen.getByDisplayValue(/All Statuses/i);
    fireEvent.change(statusFilter, { target: { value: 'active' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/subscriptions?status=active&page=1&limit=20', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });
});

describe('Admin AuditLogsPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('renders audit logs list', async () => {
    const mockLogs = [
      {
        log_id: '1',
        user: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
        action_type: 'CREATE',
        entity_type: 'subscription',
        details: 'Created new subscription',
        timestamp: '2024-01-01T10:00:00Z',
        ip_address: '192.168.1.1'
      },
      {
        log_id: '2',
        user: { first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
        action_type: 'UPDATE',
        entity_type: 'user',
        details: 'Updated profile information',
        timestamp: '2024-01-01T11:00:00Z',
        ip_address: '192.168.1.2'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ logs: mockLogs, total: 2 }),
    });

    render(
      <TestWrapper>
        <AuditLogsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
      expect(screen.getByText(/CREATE/i)).toBeInTheDocument();
      expect(screen.getByText(/UPDATE/i)).toBeInTheDocument();
      expect(screen.getByText(/subscription/i)).toBeInTheDocument();
      expect(screen.getByText(/user/i)).toBeInTheDocument();
    });
  });

  test('filters logs by action type', async () => {
    const mockLogs = [];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ logs: mockLogs, total: 0 }),
    });

    render(
      <TestWrapper>
        <AuditLogsPage />
      </TestWrapper>
    );

    const actionFilter = screen.getByDisplayValue(/All Actions/i);
    fireEvent.change(actionFilter, { target: { value: 'CREATE' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/audit-logs?action_type=CREATE&page=1&limit=50', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });

  test('filters logs by entity type', async () => {
    const mockLogs = [];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ logs: mockLogs, total: 0 }),
    });

    render(
      <TestWrapper>
        <AuditLogsPage />
      </TestWrapper>
    );

    const entityFilter = screen.getByDisplayValue(/All Entities/i);
    fireEvent.change(entityFilter, { target: { value: 'subscription' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/audit-logs?entity_type=subscription&page=1&limit=50', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });
});

describe('Admin ReportsPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('renders reports dashboard', async () => {
    const mockRevenueData = [
      { month: 'Jan', revenue: 100000, subscriptions: 80 },
      { month: 'Feb', revenue: 125000, subscriptions: 89 }
    ];

    const mockChurnData = [
      { month: 'Jan', churn_rate: 4.5 },
      { month: 'Feb', churn_rate: 5.2 }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockRevenueData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockChurnData,
      });

    render(
      <TestWrapper>
        <ReportsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Revenue Trends/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription Growth/i)).toBeInTheDocument();
      expect(screen.getByText(/Churn Analysis/i)).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });
  });

  test('handles date range selection', async () => {
    const mockData = [];

    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    render(
      <TestWrapper>
        <ReportsPage />
      </TestWrapper>
    );

    const dateRangeSelect = screen.getByDisplayValue(/Last 30 Days/i);
    fireEvent.change(dateRangeSelect, { target: { value: '90' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/admin/reports/revenue?days=90', {
        headers: {
          'Authorization': 'Bearer admin-token'
        }
      });
    });
  });

  test('exports report data', async () => {
    const mockData = [
      { month: 'Jan', revenue: 100000 },
      { month: 'Feb', revenue: 125000 }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    // Mock URL.createObjectURL and document.createElement
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockLink = {
      click: jest.fn(),
      setAttribute: jest.fn(),
    };
    document.createElement = jest.fn(() => mockLink);
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();

    render(
      <TestWrapper>
        <ReportsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const exportButton = screen.getByText(/Export CSV/i);
      fireEvent.click(exportButton);
    });

    expect(mockLink.click).toHaveBeenCalled();
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'admin-token');
  });

  test('handles unauthorized access', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Unauthorized' }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Unauthorized access/i)).toBeInTheDocument();
    });
  });

  test('handles forbidden access', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({ error: 'Forbidden' }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Access denied/i)).toBeInTheDocument();
    });
  });

  test('handles server errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Internal server error' }),
    });

    render(
      <TestWrapper>
        <UsersPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load data/i)).toBeInTheDocument();
    });
  });
});

describe('Admin Context', () => {
  test('provides admin state and functions', () => {
    const TestComponent = () => {
      const { users, subscriptions, loading } = useAdmin();
      return (
        <div>
          <span>{loading ? 'Loading' : 'Loaded'}</span>
          <span>Users: {users.length}</span>
          <span>Subscriptions: {subscriptions.length}</span>
        </div>
      );
    };

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(screen.getByText(/Users: 0/i)).toBeInTheDocument();
    expect(screen.getByText(/Subscriptions: 0/i)).toBeInTheDocument();
  });
});

