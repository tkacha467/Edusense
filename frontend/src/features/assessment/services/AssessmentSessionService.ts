import { assessmentSessionApi } from '../api/assessmentSessionApi';
import type { 
  AssessmentSession, 
  AssessmentSessionCreatePayload 
} from '../types/assessmentSession';

export class AssessmentSessionService {
  private static LOCAL_STORAGE_KEY = 'edusense_active_session_id';

  // Development Logging helper
  private static log(event: string, details?: any) {
    console.log(`[Assessment Session Manager] Event: ${event}`, details || '');
  }

  // Get active session ID stored locally for recovery
  static getStoredSessionId(): string | null {
    return localStorage.getItem(this.LOCAL_STORAGE_KEY);
  }

  // Clear active session ID stored locally
  static clearStoredSession() {
    localStorage.removeItem(this.LOCAL_STORAGE_KEY);
    this.log('Session Cleared from storage');
  }

  // Persist session ID
  static storeSessionId(sessionId: string) {
    localStorage.setItem(this.LOCAL_STORAGE_KEY, sessionId);
    this.log('Session Stored', { sessionId });
  }

  // Initialize/Start a new session safely
  static async initializeSession(payload: AssessmentSessionCreatePayload): Promise<AssessmentSession> {
    this.log('Initializing Session', payload);
    
    // 1. Check if there is already an active session to prevent duplicates
    const currentActive = await assessmentSessionApi.getCurrentSession();
    if (currentActive) {
      this.log('Duplicate Session Blocked. Redirecting to existing active session.', currentActive.id);
      this.storeSessionId(currentActive.id);
      return currentActive;
    }

    // 2. Create the session
    const session = await assessmentSessionApi.createSession(payload);
    this.log('Session Created', session);

    // 3. Start the session on the backend
    const startedSession = await assessmentSessionApi.startSession(session.id);
    this.log('Session Started', startedSession);

    // 4. Persist the session ID for crash recovery
    this.storeSessionId(startedSession.id);

    return startedSession;
  }

  // Recover active session from history or storage
  static async recoverActiveSession(): Promise<AssessmentSession | null> {
    this.log('Attempting Session Recovery');
    
    // First try database check
    try {
      const activeDbSession = await assessmentSessionApi.getCurrentSession();
      if (activeDbSession) {
        this.log('Active Session Recovered from DB', activeDbSession);
        this.storeSessionId(activeDbSession.id);
        return activeDbSession;
      }
    } catch (e) {
      this.log('Failed to check active DB session', e);
    }

    // Fallback to local storage key
    const storedId = this.getStoredSessionId();
    if (storedId) {
      try {
        const sessionDetails = await assessmentSessionApi.getSession(storedId);
        if (sessionDetails.status === 'in_progress') {
          this.log('Active Session Recovered from Storage ID', sessionDetails);
          return sessionDetails;
        }
      } catch (e) {
        this.log('Failed to recover session from stored ID', e);
        this.clearStoredSession();
      }
    }

    this.log('No Active Session Found for Recovery');
    return null;
  }

  // Cancel/Abandon session
  static async cancelSession(sessionId: string): Promise<AssessmentSession> {
    this.log('Session Cancelled', { sessionId });
    const session = await assessmentSessionApi.cancelSession(sessionId);
    this.clearStoredSession();
    return session;
  }

  // Complete session
  static async completeSession(sessionId: string, responses: any[]): Promise<any> {
    this.log('Session Submitted for Evaluation', { sessionId, responseCount: responses.length });
    const result = await assessmentSessionApi.completeSession(sessionId, responses);
    this.log('Session Completed & Evaluated', result);
    this.clearStoredSession();
    return result;
  }
}
