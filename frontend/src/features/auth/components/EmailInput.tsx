import React from 'react';
import { Mail } from 'lucide-react';
import { FormControl, FormItem, FormLabel, FormMessage } from '../../../components/ui/Form';
import { Input } from '../../../components/ui/Input';

interface EmailInputProps {
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
}

export const EmailInput: React.FC<EmailInputProps> = React.memo(({
  field,
  label = "Email Address",
  placeholder = "user@school.edu",
  disabled = false,
}) => {
  return (
    <FormItem>
      <FormLabel>{label}</FormLabel>
      <FormControl>
        <div className="relative">
          <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          <Input
            className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white text-base"
            placeholder={placeholder}
            disabled={disabled}
            type="email"
            autoComplete="email"
            aria-label={label}
            {...field}
          />
        </div>
      </FormControl>
      <FormMessage />
    </FormItem>
  );
});

EmailInput.displayName = 'EmailInput';
