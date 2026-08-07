import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HelmetProvider, Helmet } from "react-helmet-async";
import Index from "./pages/Index";
import GetHelp from "./pages/GetHelp";
import Partners from "./pages/Partners";
import Impact from "./pages/Impact";
import GetInvolved from "./pages/GetInvolved";
import Donate from "./pages/Donate";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Volunteer from "./pages/Volunteer";
import HousingStabilizationModel from "./pages/HousingStabilizationModel";
import ForCounties from "./pages/ForCounties";
import LandPartnerships from "./pages/LandPartnerships";
import FundAPilot from "./pages/FundAPilot";
import Veterans from "./pages/Veterans";
import DignityFirstModel from "./pages/DignityFirstModel";
import CorporateSponsors from "./pages/CorporateSponsors";
import EmployerPartners from "./pages/EmployerPartners";
import ThankYou from "./pages/ThankYou";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Helmet>
          <title>Klear Path | Workforce-Driven Housing Stability</title>
          <meta name="description" content="Klear Path partners with counties, landowners, funders, and workforce organizations to build scalable housing stability and employment outcomes in Bucks & Montgomery Counties, PA." />
          <meta name="keywords" content="workforce housing, housing stability programs, county housing partnerships, land donation nonprofit, pilot funding, homelessness prevention" />
        </Helmet>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/get-help" element={<GetHelp />} />
            <Route path="/help" element={<Navigate to="/get-help" replace />} />
            <Route path="/model" element={<Navigate to="/housing-stabilization-model" replace />} />
            <Route path="/housing-stabilization-model" element={<HousingStabilizationModel />} />
            <Route path="/partners" element={<Partners />} />
            <Route path="/for-counties" element={<ForCounties />} />
            <Route path="/land-partnerships" element={<LandPartnerships />} />
            <Route path="/fund-a-pilot" element={<FundAPilot />} />
            <Route path="/veterans" element={<Veterans />} />
            <Route path="/dignity-first-model" element={<DignityFirstModel />} />
            <Route path="/corporate-sponsors" element={<CorporateSponsors />} />
            <Route path="/employer-partners" element={<EmployerPartners />} />
            <Route path="/impact" element={<Impact />} />
            <Route path="/get-involved" element={<GetInvolved />} />
            <Route path="/donate" element={<Donate />} />
            <Route path="/thank-you" element={<ThankYou />} />
            <Route path="/volunteer" element={<Volunteer />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/privacy" element={<Navigate to="/privacy-policy" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
