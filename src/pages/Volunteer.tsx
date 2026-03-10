import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Users, Heart, Hammer, Utensils, BookOpen, Clock, CheckCircle } from "lucide-react";

const Volunteer = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    interests: [] as string[],
    availability: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    toast({
      title: "Thank you for your interest!",
      description: "We'll be in touch soon to discuss volunteer opportunities.",
    });
    setFormData({ name: "", email: "", phone: "", interests: [], availability: "", message: "" });
    setIsSubmitting(false);
  };

  const toggleInterest = (interest: string) => {
    setFormData((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const opportunities = [
    { icon: Hammer, title: "Community Outreach", description: "Help connect individuals with housing stabilization resources and community services." },
    { icon: Utensils, title: "Program Support", description: "Assist with daily operations, meal coordination, and participant support activities." },
    { icon: BookOpen, title: "Skills & Mentorship", description: "Share professional skills, provide resume help, or mentor program participants." },
    { icon: Users, title: "Events & Fundraising", description: "Help organize community events, awareness campaigns, and fundraising initiatives." },
  ];

  return (
    <Layout>
      <Helmet>
        <title>Volunteer With Klear Path | Housing Stabilization Support</title>
        <meta name="description" content="Volunteer with Klear Path to support housing stabilization initiatives and community outreach in Bucks and Montgomery Counties, Pennsylvania." />
        <meta name="keywords" content="volunteer homelessness, housing stability services, community housing partnerships, homelessness prevention initiatives" />
      </Helmet>

      {/* Hero */}
      <section className="py-16 lg:py-24 bg-primary text-primary-foreground">
        <div className="container-wide section-padding">
          <div className="max-w-3xl">
            <h1 className="text-4xl lg:text-5xl font-serif font-bold mb-6">
              Volunteer With Klear Path
            </h1>
            <p className="text-xl text-primary-foreground/90 leading-relaxed">
              Volunteers help support housing stabilization initiatives and community outreach.
              Your time and skills make a direct impact on individuals working toward stability.
            </p>
          </div>
        </div>
      </section>

      {/* Opportunities */}
      <section className="py-16 lg:py-24">
        <div className="container-wide section-padding">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
              Volunteer Opportunities
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Whether you have a few hours a month or want to make a regular commitment, there are
              meaningful ways to contribute.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {opportunities.map((opp) => (
              <div key={opp.title} className="bg-card rounded-xl p-6 shadow-soft border border-border text-center">
                <opp.icon className="w-10 h-10 text-primary mx-auto mb-4" />
                <h3 className="font-serif font-semibold text-lg mb-2">{opp.title}</h3>
                <p className="text-sm text-muted-foreground">{opp.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center">
            <div className="inline-flex items-center gap-2 text-muted-foreground bg-accent rounded-full px-6 py-3">
              <Clock className="w-4 h-4" />
              <span className="text-sm">Flexible scheduling — weekdays, evenings, and weekends</span>
            </div>
          </div>
        </div>
      </section>

      {/* Interest Form */}
      <section className="py-16 lg:py-24 bg-secondary">
        <div className="container-wide section-padding">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-3xl lg:text-4xl font-serif font-semibold text-foreground mb-4">
                Volunteer Interest Form
              </h2>
              <p className="text-lg text-muted-foreground">
                Tell us about yourself and how you'd like to help. We'll follow up with next steps.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="bg-card rounded-2xl p-8 shadow-medium border border-border">
              <div className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input id="name" required value={formData.name} onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))} placeholder="Your name" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input id="email" type="email" required value={formData.email} onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))} placeholder="you@example.com" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" type="tel" value={formData.phone} onChange={(e) => setFormData((p) => ({ ...p, phone: e.target.value }))} placeholder="(215) 555-1234" />
                </div>

                <div className="space-y-3">
                  <Label>I'm interested in:</Label>
                  <div className="flex flex-wrap gap-2">
                    {["Community Outreach", "Program Support", "Skills & Mentorship", "Events & Fundraising", "Other"].map((option) => (
                      <button
                        key={option}
                        type="button"
                        onClick={() => toggleInterest(option)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                          formData.interests.includes(option) ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        }`}
                      >
                        {formData.interests.includes(option) && <CheckCircle className="w-4 h-4 inline mr-1" />}
                        {option}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="availability">Availability</Label>
                  <Input id="availability" value={formData.availability} onChange={(e) => setFormData((p) => ({ ...p, availability: e.target.value }))} placeholder="e.g. Weekends, 4 hours/month" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Anything else? (optional)</Label>
                  <Textarea id="message" value={formData.message} onChange={(e) => setFormData((p) => ({ ...p, message: e.target.value }))} placeholder="Share any skills, experience, or questions..." rows={4} />
                </div>

                <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? "Submitting..." : "Submit Volunteer Interest"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Why Volunteer */}
      <section className="py-16 lg:py-20">
        <div className="container-wide section-padding text-center">
          <Heart className="w-12 h-12 text-primary mx-auto mb-4" />
          <h2 className="text-3xl font-serif font-semibold text-foreground mb-4">
            Why Volunteer With Klear Path?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Every hour you contribute directly supports housing stabilization programs and
            homelessness prevention initiatives in your community. Together, we can build
            pathways from crisis to stability.
          </p>
        </div>
      </section>
    </Layout>
  );
};

export default Volunteer;
