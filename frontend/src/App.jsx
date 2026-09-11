import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import DatasetIntegrity from './pages/DatasetIntegrity';
import ModelIntegrity from './pages/ModelIntegrity';
import InferenceVerification from './pages/InferenceVerification';
import DistributionShift from './pages/DistributionShift';
import SecurityLab from './pages/SecurityLab';
import EvidenceExplorer from './pages/EvidenceExplorer';
import AuditTrail from './pages/AuditTrail';
import AssuranceReports from './pages/AssuranceReports';
import SystemInformation from './pages/SystemInformation';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"             element={<Dashboard />} />
        <Route path="dataset-integrity"     element={<DatasetIntegrity />} />
        <Route path="model-integrity"       element={<ModelIntegrity />} />
        <Route path="inference-verification"element={<InferenceVerification />} />
        <Route path="distribution-shift"    element={<DistributionShift />} />
        <Route path="security-lab"          element={<SecurityLab />} />
        <Route path="evidence-explorer"     element={<EvidenceExplorer />} />
        <Route path="audit-trail"           element={<AuditTrail />} />
        <Route path="assurance-reports"     element={<AssuranceReports />} />
        <Route path="system-information"    element={<SystemInformation />} />
        <Route path="*"                     element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
