import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import { SubscriptionProvider } from '../src/contexts/SubscriptionContext';
import App from '../src/App';
import LoginPage from '../src/pages/LoginPage';
import RegisterPage from '../src/pages/RegisterPage';
import DashboardPage from '../src/pages/DashboardPage';
import ProductsPage from '../src/pages/ProductsPage';
import SubscriptionsPage from '../src/pages/SubscriptionsPage';
import ProfilePage from '../src/pages/ProfilePage';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock React Router
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      <SubscriptionProvider>
        {children}
      </SubscriptionProvider>
    </AuthProvider>
  </BrowserRouter>
);

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders homepage by default', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    expect(screen.getByText(/SubscriptionPro/i)).toBeInTheDocument();
    expect(screen.getByText(/Simplify Your Subscription Management/i)).toBeInTheDocument();
  });

  test('renders navigation menu', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    expect(screen.getByText(/Home/i)).toBeInTheDocument();
    expect(screen.getByText(/Products/i)).toBeInTheDocument();
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
    expect(screen.getByText(/Register/i)).toBeInTheDocument();
  });
});

describe('LoginPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders login form', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });

  test('handles form submission', async () => {
    const mockResponse = {
      access_token: 'mock-token',
      user: { id: '1', email: 'test@example.com', first_name: 'Test' }
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

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123'
        })
      });
    });
  });

  test('displays error message on failed login', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Invalid credentials' }),
    });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Sign In/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Password is required/i)).toBeInTheDocument();
    });
  });
});

describe('RegisterPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders registration form', () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
  });

  test('handles successful registration', async () => {
    const mockResponse = {
      access_token: 'mock-token',
      user: { id: '1', email: 'test@example.com', first_name: 'Test' }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const firstNameInput = screen.getByLabelText(/First Name/i);
    const lastNameInput = screen.getByLabelText(/Last Name/i);
    const submitButton = screen.getByRole('button', { name: /Create Account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(firstNameInput, { target: { value: 'Test' } });
    fireEvent.change(lastNameInput, { target: { value: 'User' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
          first_name: 'Test',
          last_name: 'User',
          phone_number: '',
          date_of_birth: '',
          address_line1: '',
          address_line2: '',
          city: '',
          state: '',
          postal_code: '',
          country: 'India'
        })
      });
    });
  });

  test('validates email format', async () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Create Account/i });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  test('validates password strength', async () => {
    render(
      <TestWrapper>
        <RegisterPage />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText(/Password/i);
    const submitButton = screen.getByRole('button', { name: /Create Account/i });

    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });
});

describe('DashboardPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    
    // Mock localStorage for auth token
    Storage.prototype.getItem = jest.fn(() => 'mock-token');
  });

  test('renders dashboard with user data', async () => {
    const mockUserData = {
      first_name: 'Test',
      last_name: 'User',
      email: 'test@example.com'
    };

    const mockSubscriptions = [
      {
        subscription_id: '1',
        product: { name: 'Premium Coffee' },
        status: 'active',
        next_delivery_date: '2024-02-01'
      }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUserData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ subscriptions: mockSubscriptions, total: 1 }),
      });

    render(
      <TestWrapper>
        <DashboardPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Welcome back, Test!/i)).toBeInTheDocument();
      expect(screen.getByText(/Premium Coffee/i)).toBeInTheDocument();
    });
  });

  test('displays loading state', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(
      <TestWrapper>
        <DashboardPage />
      </TestWrapper>
    );

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });
});

describe('ProductsPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders products list', async () => {
    const mockProducts = [
      {
        product_id: '1',
        name: 'Premium Coffee',
        description: 'Monthly coffee delivery',
        price: 2999,
        category: 'Food & Beverage'
      },
      {
        product_id: '2',
        name: 'Organic Vegetables',
        description: 'Weekly vegetable box',
        price: 1499,
        category: 'Food & Beverage'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ products: mockProducts, total: 2 }),
    });

    render(
      <TestWrapper>
        <ProductsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Premium Coffee/i)).toBeInTheDocument();
      expect(screen.getByText(/Organic Vegetables/i)).toBeInTheDocument();
    });
  });

  test('handles product search', async () => {
    const mockProducts = [
      {
        product_id: '1',
        name: 'Premium Coffee',
        description: 'Monthly coffee delivery',
        price: 2999,
        category: 'Food & Beverage'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ products: mockProducts, total: 1 }),
    });

    render(
      <TestWrapper>
        <ProductsPage />
      </TestWrapper>
    );

    const searchInput = screen.getByPlaceholderText(/Search products/i);
    fireEvent.change(searchInput, { target: { value: 'coffee' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/products?search=coffee&page=1&limit=12');
    });
  });

  test('handles category filter', async () => {
    const mockProducts = [];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ products: mockProducts, total: 0 }),
    });

    render(
      <TestWrapper>
        <ProductsPage />
      </TestWrapper>
    );

    const categorySelect = screen.getByDisplayValue(/All Categories/i);
    fireEvent.change(categorySelect, { target: { value: 'Food & Beverage' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/products?category=Food%20%26%20Beverage&page=1&limit=12');
    });
  });
});

describe('SubscriptionsPage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'mock-token');
  });

  test('renders subscriptions list', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        next_delivery_date: '2024-02-01',
        amount: 2999
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
      expect(screen.getByText(/Premium Coffee/i)).toBeInTheDocument();
      expect(screen.getByText(/Active/i)).toBeInTheDocument();
      expect(screen.getByText(/Monthly/i)).toBeInTheDocument();
    });
  });

  test('handles subscription pause', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        next_delivery_date: '2024-02-01',
        amount: 2999
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
      const pauseButton = screen.getByText(/Pause/i);
      fireEvent.click(pauseButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/subscriptions/1/pause', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-token'
        },
        body: JSON.stringify({ reason: 'User requested pause' })
      });
    });
  });

  test('handles subscription cancellation', async () => {
    const mockSubscriptions = [
      {
        subscription_id: '1',
        product: { name: 'Premium Coffee' },
        status: 'active',
        frequency: 'monthly',
        next_delivery_date: '2024-02-01',
        amount: 2999
      }
    ];

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ subscriptions: mockSubscriptions, total: 1 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockSubscriptions[0], status: 'canceled' }),
      });

    render(
      <TestWrapper>
        <SubscriptionsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const cancelButton = screen.getByText(/Cancel/i);
      fireEvent.click(cancelButton);
    });

    // Confirm cancellation in modal
    await waitFor(() => {
      const confirmButton = screen.getByText(/Confirm Cancellation/i);
      fireEvent.click(confirmButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/subscriptions/1/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-token'
        },
        body: JSON.stringify({ reason: 'User requested cancellation', immediate: false })
      });
    });
  });
});

describe('ProfilePage Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    Storage.prototype.getItem = jest.fn(() => 'mock-token');
  });

  test('renders profile form with user data', async () => {
    const mockUserData = {
      first_name: 'Test',
      last_name: 'User',
      email: 'test@example.com',
      phone_number: '+91-9876543210',
      address_line1: '123 Test Street',
      city: 'Mumbai',
      state: 'Maharashtra',
      postal_code: '400001',
      country: 'India'
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUserData,
    });

    render(
      <TestWrapper>
        <ProfilePage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test')).toBeInTheDocument();
      expect(screen.getByDisplayValue('User')).toBeInTheDocument();
      expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
    });
  });

  test('handles profile update', async () => {
    const mockUserData = {
      first_name: 'Test',
      last_name: 'User',
      email: 'test@example.com'
    };

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUserData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockUserData, first_name: 'Updated' }),
      });

    render(
      <TestWrapper>
        <ProfilePage />
      </TestWrapper>
    );

    await waitFor(() => {
      const firstNameInput = screen.getByDisplayValue('Test');
      fireEvent.change(firstNameInput, { target: { value: 'Updated' } });
      
      const saveButton = screen.getByText(/Save Changes/i);
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-token'
        },
        body: expect.stringContaining('"first_name":"Updated"')
      });
    });
  });

  test('handles password change', async () => {
    const mockUserData = {
      first_name: 'Test',
      last_name: 'User',
      email: 'test@example.com'
    };

    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUserData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Password changed successfully' }),
      });

    render(
      <TestWrapper>
        <ProfilePage />
      </TestWrapper>
    );

    await waitFor(() => {
      // Switch to Security tab
      const securityTab = screen.getByText(/Security/i);
      fireEvent.click(securityTab);
    });

    const currentPasswordInput = screen.getByLabelText(/Current Password/i);
    const newPasswordInput = screen.getByLabelText(/New Password/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm New Password/i);
    const changePasswordButton = screen.getByText(/Change Password/i);

    fireEvent.change(currentPasswordInput, { target: { value: 'oldpassword' } });
    fireEvent.change(newPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(changePasswordButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/users/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-token'
        },
        body: JSON.stringify({
          current_password: 'oldpassword',
          new_password: 'newpassword123'
        })
      });
    });
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('handles network errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    render(
      <TestWrapper>
        <ProductsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load products/i)).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Internal server error' }),
    });

    render(
      <TestWrapper>
        <ProductsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load products/i)).toBeInTheDocument();
    });
  });
});

describe('Authentication Context', () => {
  test('provides authentication state', () => {
    const TestComponent = () => {
      const { user, isAuthenticated } = useAuth();
      return (
        <div>
          <span>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</span>
          {user && <span>User: {user.email}</span>}
        </div>
      );
    };

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(screen.getByText(/Not authenticated/i)).toBeInTheDocument();
  });
});

describe('Subscription Context', () => {
  test('provides subscription management functions', () => {
    const TestComponent = () => {
      const { subscriptions, loading } = useSubscription();
      return (
        <div>
          <span>{loading ? 'Loading' : 'Loaded'}</span>
          <span>Subscriptions: {subscriptions.length}</span>
        </div>
      );
    };

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(screen.getByText(/Subscriptions: 0/i)).toBeInTheDocument();
  });
});

