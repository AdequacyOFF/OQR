import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'danger' | 'secondary';
  loading?: boolean;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const variantClass = variant === 'primary' ? 'btn' :
    variant === 'danger' ? 'btn btn-danger' :
    'btn btn-secondary';

  return (
    <button
      className={`${variantClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />}
      {children}
    </button>
  );
};

export default Button;
