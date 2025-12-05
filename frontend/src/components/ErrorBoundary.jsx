import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './ui';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full">
            <div className="bg-white shadow-lg rounded-lg p-8 text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Oops! Something went wrong
              </h1>
              <p className="text-gray-600 mb-6">
                We apologize for the inconvenience. An unexpected error has occurred.
              </p>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6 text-left">
                  <details className="bg-gray-50 rounded p-4">
                    <summary className="cursor-pointer font-semibold text-sm text-gray-700 mb-2">
                      Error Details (Development Only)
                    </summary>
                    <div className="text-xs text-gray-600 font-mono mt-2">
                      <p className="font-semibold text-red-600">{this.state.error.toString()}</p>
                      {this.state.errorInfo && (
                        <pre className="mt-2 overflow-auto whitespace-pre-wrap">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      )}
                    </div>
                  </details>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                >
                  Reload Page
                </Button>
                <Button onClick={this.handleReset}>
                  Go to Dashboard
                </Button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
