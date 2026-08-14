import React from 'react';
import type { UserRoleType as Role } from '../../../types';

interface RoleHeaderProps {
  title: string;
  subtitle: string;
  role?: Role | 'faculty';
}

export const RoleHeader: React.FC<RoleHeaderProps> = React.memo(({ title, subtitle }) => {
  return (
    <div className="space-y-2">
      <h2 className="text-3xl font-bold tracking-tight text-gray-900">{title}</h2>
      <p className="text-gray-500">{subtitle}</p>
    </div>
  );
});

RoleHeader.displayName = 'RoleHeader';
