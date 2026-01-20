import React from 'react';

const PrivacyPolicy = ({ onBack }) => {
  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '40px 20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <button 
        onClick={onBack}
        style={{
          marginBottom: '20px',
          padding: '8px 16px',
          backgroundColor: '#f3f4f6',
          color: '#374151',
          border: '1px solid #d1d5db',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        ← Back
      </button>

      <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1e293b', marginBottom: '24px' }}>
        Privacy Policy
      </h1>

      <div style={{ 
        backgroundColor: '#f8fafc', 
        border: '1px solid #e2e8f0', 
        borderRadius: '12px', 
        padding: '24px',
        marginBottom: '24px'
      }}>
        <p style={{ fontSize: '16px', lineHeight: '1.7', color: '#475569' }}>
          This application is a demo AI-powered hiring platform.
        </p>
      </div>

      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1e293b', marginBottom: '16px' }}>
          Information We Collect
        </h2>
        <p style={{ fontSize: '15px', lineHeight: '1.7', color: '#475569' }}>
          We only collect basic LinkedIn profile information for authentication purposes. This includes:
        </p>
        <ul style={{ fontSize: '15px', lineHeight: '1.8', color: '#475569', paddingLeft: '20px' }}>
          <li>Your name (first and last name)</li>
          <li>Your email address</li>
          <li>Your LinkedIn profile picture URL</li>
          <li>Your LinkedIn profile ID (for authentication purposes only)</li>
        </ul>
      </section>

      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1e293b', marginBottom: '16px' }}>
          How We Use Your Information
        </h2>
        <p style={{ fontSize: '15px', lineHeight: '1.7', color: '#475569' }}>
          Your LinkedIn information is used solely for:
        </p>
        <ul style={{ fontSize: '15px', lineHeight: '1.8', color: '#475569', paddingLeft: '20px' }}>
          <li>Authenticating your identity when you log in</li>
          <li>Displaying your profile information within the application</li>
          <li>Enabling you to share job postings on LinkedIn (with your explicit action)</li>
        </ul>
      </section>

      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1e293b', marginBottom: '16px' }}>
          Data Protection
        </h2>
        <ul style={{ fontSize: '15px', lineHeight: '1.8', color: '#475569', paddingLeft: '20px' }}>
          <li>No data is sold or shared with third parties</li>
          <li>OAuth tokens are stored securely and encrypted</li>
          <li>We do not store your LinkedIn password</li>
          <li>You can disconnect your LinkedIn account at any time</li>
        </ul>
      </section>

      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1e293b', marginBottom: '16px' }}>
          Data Retention
        </h2>
        <p style={{ fontSize: '15px', lineHeight: '1.7', color: '#475569' }}>
          Your authentication tokens are stored only for the duration of your session and expire after 60 days. 
          You can revoke access at any time by disconnecting your LinkedIn account or through LinkedIn's privacy settings.
        </p>
      </section>

      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#1e293b', marginBottom: '16px' }}>
          Contact Us
        </h2>
        <p style={{ fontSize: '15px', lineHeight: '1.7', color: '#475569' }}>
          If you have any questions about this Privacy Policy, please contact us at privacy@gccHiringsystem.com
        </p>
      </section>

      <div style={{
        padding: '16px',
        backgroundColor: '#fef3c7',
        border: '1px solid #fcd34d',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#92400e'
      }}>
        <strong>Demo Notice:</strong> This is a demonstration application. In production, 
        additional security measures and comprehensive data protection policies would be implemented.
      </div>

      <p style={{ marginTop: '32px', fontSize: '13px', color: '#94a3b8', textAlign: 'center' }}>
        Last updated: December 2025
      </p>
    </div>
  );
};

export default PrivacyPolicy;
