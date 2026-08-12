import React, { useState } from 'react';
import { Lock, Eye, EyeOff } from 'lucide-react';
import { FormControl, FormItem, FormLabel, FormMessage } from '../../../components/ui/Form';
import { Input } from '../../../components/ui/Input';

interface PasswordInputProps {
  field: {
    name: string;
    value: string;
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    onBlur: () => void;
    ref: React.Ref<HTMLInputElement>;
  };
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  autoComplete?: string;
}

export const PasswordInput: React.FC<PasswordInputProps> = React.memo(({
  field,
  label = "Password",
  placeholder = "••••••••",
  disabled = false,
  autoComplete = "current-password",
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const toggleShowPassword = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <FormItem>
      <FormLabel>{label}</FormLabel>
      <FormControl>
        <div className="relative">
          <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          <Input
            type={showPassword ? "text" : "password"}
            className="pl-10 pr-10 h-12 bg-gray-50 border-gray-200 focus:bg-white text-base"
            placeholder={placeholder}
            disabled={disabled}
            autoComplete={autoComplete}
            aria-label={label}
            {...field}
          />
          <button
            type="button"
            className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 focus:outline-none"
            onClick={toggleShowPassword}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
      </FormControl>
      <FormMessage />
    </FormItem>
  );
});

PasswordInput.displayName = 'PasswordInput';
