import { useState } from "react";
import { Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function EmailCapture() {
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
  };

  return (
    <section className="py-16 bg-secondary border-y border-border" data-section="email-capture">
      <div className="container-wide section-padding">
        <div className="grid lg:grid-cols-[1fr_1.1fr] gap-8 items-center">
          <div>
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
              <Mail className="w-6 h-6 text-primary" />
            </div>
            <h2 className="text-3xl font-serif font-bold text-foreground mb-4">
              Stay Connected To The Mission
            </h2>
            <p className="text-muted-foreground leading-relaxed max-w-xl">
              Receive updates, impact stories, volunteer opportunities, and ways to support long-term housing stability initiatives.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="bg-card border border-border rounded-2xl p-6 shadow-soft">
            <div className="grid sm:grid-cols-2 gap-3 mb-4">
              <Input
                placeholder="First name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
              <Input
                type="email"
                required
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <Button type="submit" data-cta="email-capture-submit">
              Stay Connected
            </Button>

            {submitted && (
              <p className="text-sm text-primary font-medium mt-4">
                You’re on the list. More updates coming soon.
              </p>
            )}

            <p className="text-xs text-muted-foreground mt-4">
              No spam. Just mission updates, impact milestones, and opportunities to help.
            </p>
          </form>
        </div>
      </div>
    </section>
  );
}
