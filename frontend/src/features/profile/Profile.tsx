import { useAuth } from '../../contexts/AuthContext';
import { UserRole } from '../../types';
import React, { useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { profileSchema } from '../../utils/validations';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '../../components/ui/Form';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Camera, Mail, Shield, User } from 'lucide-react';
import { z } from 'zod';
import { useToast } from '../../contexts/ToastContext';

export function Profile() {
  const { currentUser, updateProfile } = useAuth();
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarPreview, setAvatarPreview] = useState(currentUser?.avatarUrl || '');

  const firstName = currentUser?.fullName?.split(' ')[0] || '';
  const lastName = currentUser?.fullName?.split(' ').slice(1).join(' ') || '';
  
  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: firstName,
      lastName: lastName,
      email: currentUser?.email || '',
      role: (currentUser?.role === UserRole.FACULTY ? 'Faculty' : 'Student') as any,
      bio: currentUser?.bio || '',
    },
  });

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        showToast('Image size must be less than 2MB', 'error');
        return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const onSubmit = async (values: z.infer<typeof profileSchema>) => {
    try {
      await updateProfile({
        fullName: `${values.firstName} ${values.lastName}`,
        bio: values.bio,
        avatarUrl: avatarPreview,
      });
      showToast('Profile updated successfully', 'success');
    } catch (error) {
      showToast('Failed to update profile', 'error');
      console.error(error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Profile</h1>
        <p className="text-muted-foreground mt-1">Manage your public profile and personal details.</p>
      </div>

      <div className="bg-white border rounded-2xl shadow-sm overflow-hidden">
        {/* Banner */}
        <div className="h-32 bg-gradient-to-r from-primary/20 to-secondary/20"></div>
        
        <div className="px-8 pb-8">
          {/* Avatar */}
          <div className="relative -mt-12 mb-8 flex justify-between items-end">
            <div className="relative group">
              <div className="w-24 h-24 rounded-2xl bg-white p-1 shadow-md">
                <div className="w-full h-full rounded-xl bg-gray-100 flex items-center justify-center border overflow-hidden">
                  {avatarPreview ? (
                    <img src={avatarPreview} alt="Profile Preview" className="w-full h-full object-cover" />
                  ) : (
                    <User className="w-10 h-10 text-gray-400" />
                  )}
                </div>
              </div>
              <button 
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-2 right-2 p-1.5 bg-primary text-white rounded-lg shadow-sm hover:bg-primary/90 transition-colors cursor-pointer"
                title="Upload Profile Photo"
              >
                <Camera className="w-4 h-4" />
              </button>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*"
                onChange={handleImageUpload}
              />
            </div>
            
            <div className="flex gap-3">
              <Button type="button" variant="outline" onClick={() => {
                form.reset();
                setAvatarPreview(currentUser?.avatarUrl || '');
              }}>Cancel</Button>
              <Button onClick={form.handleSubmit(onSubmit)}>Save Changes</Button>
            </div>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid sm:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="firstName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input placeholder="John" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="lastName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email Address</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input className="pl-9" placeholder="john@example.com" {...field} disabled />
                      </div>
                    </FormControl>
                    <FormDescription>Your email address is managed by your organization.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="role"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Role</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Shield className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input className="pl-9 bg-gray-50" {...field} disabled />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="bio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Biography</FormLabel>
                    <FormControl>
                      <textarea 
                        className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                        placeholder="Tell us a little bit about yourself" 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </div>
      </div>
    </div>
  );
}


