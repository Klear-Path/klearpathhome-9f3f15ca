import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider, Helmet } from "react-helmet-async";
import Index from "./pages/Index";
import TheModel from "./pages/TheModel";
import Partners from "./pages/Partners";
import Impact from "./pages/Impact";
import GetInvolved from "./pages/GetInvolved";
import Donate from "./pages/Donate";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Volunteer from "./pages/Volunteer";
import HousingStabilizationModel from "./pages/HousingStabilizationModel";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Helmet>
          <title>Klear Path | Housing Stabilization Programs | Bucks & Montgomery Counties</title>
          <meta name="description" content="Klear Path is a 501(c)(3) nonprofit building scalable housing stabilization programs and homelessness solutions through coordinated community partnerships in Bucks and Montgomery Counties, PA." />
          <meta name="keywords" content="housing stabilization programs, homelessness solutions nonprofit, community housing partnerships, homelessness prevention initiatives, innovative housing programs, housing stability services" />
        </Helmet>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/model" element={<TheModel />} />
            <Route path="/housing-stabilization-model" element={<HousingStabilizationModel />} />
            <Route path="/partners" element={<Partners />} />
            <Route path="/impact" element={<Impact />} />
            <Route path="/get-involved" element={<GetInvolved />} />
            <Route path="/donate" element={<Donate />} />
            <Route path="/volunteer" element={<Volunteer />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
