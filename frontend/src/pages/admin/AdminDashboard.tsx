import React, { useEffect, useState } from 'react';
import { Shield, Check, X } from 'lucide-react';
import apiClient from '../../api/apiClient';
import { useToast } from '../../contexts/ToastContext';

interface FacultyRequest {
  id: string;
  user_id: string;
  institution_id: string;
  department_id: string;
  status: string;
  submitted_at: string;
  request_number: number;
  user?: {
    email: string;
    display_name: string;
  };
}

export const AdminDashboard: React.FC = () => {
  const [requests, setRequests] = useState<FacultyRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const fetchRequests = async () => {
    try {
      const response = await apiClient.get('/admin/faculty-requests?status_filter=pending');
      setRequests(response.data);
    } catch (error) {
      showToast('Failed to load requests', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await apiClient.post(`/admin/faculty-requests/${id}/approve`, { notes: 'Approved by admin' });
      showToast('Request approved', 'success');
      fetchRequests();
    } catch (error) {
      showToast('Approval failed', 'error');
    }
  };

  const handleReject = async (id: string) => {
    try {
      await apiClient.post(`/admin/faculty-requests/${id}/reject`, { rejection_reason: 'Does not meet criteria', notes: 'Rejected by admin' });
      showToast('Request rejected', 'success');
      fetchRequests();
    } catch (error) {
      showToast('Rejection failed', 'error');
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Shield className="w-8 h-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">Pending Faculty Requests</h2>
        {requests.length === 0 ? (
          <p className="text-gray-500">No pending requests.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg">Faculty Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Institution</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Submitted</th>
                  <th className="px-4 py-3 rounded-tr-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {requests.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50/50">
                    <td className="px-4 py-3 font-medium text-gray-900">{req.user?.display_name || req.user_id}</td>
                    <td className="px-4 py-3 text-gray-600">{req.user?.email || '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{req.institution_id || '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{req.department_id || '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(req.submitted_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleApprove(req.id)}
                        className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors mr-2"
                        title="Approve"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleReject(req.id)}
                        className="p-1.5 text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
                        title="Reject"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
