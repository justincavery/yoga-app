import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatCard from '../StatCard';

describe('StatCard Component', () => {
  it('renders title and value correctly', () => {
    render(
      <StatCard
        title="Total Sessions"
        value="42"
      />
    );

    expect(screen.getByText('Total Sessions')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(
      <StatCard
        title="Practice Time"
        value="10 hours"
        subtitle="Last 30 days"
      />
    );

    expect(screen.getByText('Practice Time')).toBeInTheDocument();
    expect(screen.getByText('10 hours')).toBeInTheDocument();
    expect(screen.getByText('Last 30 days')).toBeInTheDocument();
  });

  it('renders icon when provided', () => {
    const TestIcon = () => <svg data-testid="test-icon"><circle /></svg>;

    render(
      <StatCard
        title="Streak"
        value="5 days"
        icon={<TestIcon />}
      />
    );

    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('applies variant styling for primary variant', () => {
    const { container } = render(
      <StatCard
        title="Total Sessions"
        value="42"
        variant="primary"
      />
    );

    const card = container.querySelector('[data-variant="primary"]');
    expect(card).toBeInTheDocument();
  });

  it('applies variant styling for success variant', () => {
    const { container } = render(
      <StatCard
        title="Completion Rate"
        value="95%"
        variant="success"
      />
    );

    const card = container.querySelector('[data-variant="success"]');
    expect(card).toBeInTheDocument();
  });

  it('applies variant styling for info variant', () => {
    const { container } = render(
      <StatCard
        title="Average Duration"
        value="25 min"
        variant="info"
      />
    );

    const card = container.querySelector('[data-variant="info"]');
    expect(card).toBeInTheDocument();
  });

  it('applies default variant when none specified', () => {
    const { container } = render(
      <StatCard
        title="Test"
        value="123"
      />
    );

    const card = container.querySelector('[data-variant="default"]');
    expect(card).toBeInTheDocument();
  });

  it('handles zero values', () => {
    render(
      <StatCard
        title="Sessions"
        value="0"
      />
    );

    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('handles long values without breaking layout', () => {
    render(
      <StatCard
        title="Total Time"
        value="1,234,567 minutes"
      />
    );

    expect(screen.getByText('1,234,567 minutes')).toBeInTheDocument();
  });

  it('renders with custom className when provided', () => {
    const { container } = render(
      <StatCard
        title="Test"
        value="123"
        className="custom-class"
      />
    );

    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });
});
