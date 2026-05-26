import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import Stripe from "https://esm.sh/stripe@18.5.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const ALLOWED_ORIGINS = [
  "https://klearpathhome.lovable.app",
  "https://klearpathhome.org",
  "https://www.klearpathhome.org",
];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { amount, email } = await req.json();

    const numericAmount = Number(amount);
    if (!Number.isFinite(numericAmount) || numericAmount < 1 || numericAmount > 100000) {
      return new Response(
        JSON.stringify({ error: "Please enter a donation amount between $1 and $100,000." }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    if (email && (typeof email !== "string" || email.length > 255 || !EMAIL_RE.test(email))) {
      return new Response(
        JSON.stringify({ error: "Please enter a valid email address." }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const requestOrigin = req.headers.get("origin") || "";
    const safeOrigin = ALLOWED_ORIGINS.includes(requestOrigin)
      ? requestOrigin
      : ALLOWED_ORIGINS[0];

    const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY") || "", {
      apiVersion: "2025-08-27.basil",
    });

    // Check for existing customer by email
    let customerId: string | undefined;
    if (email) {
      const customers = await stripe.customers.list({ email, limit: 1 });
      if (customers.data.length > 0) {
        customerId = customers.data[0].id;
      }
    }

    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      customer_email: customerId ? undefined : (email || undefined),
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: {
              name: "Donation to Klear Path Home",
              description: "Tax-deductible donation to Klear Path Home, Inc. (EIN: 41-3156622)",
            },
            unit_amount: Math.round(numericAmount * 100),
          },
          quantity: 1,
        },
      ],
      mode: "payment",
      success_url: `${safeOrigin}/thank-you`,
      cancel_url: `${safeOrigin}/donate`,
      submit_type: "donate",
    });

    return new Response(JSON.stringify({ url: session.url }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    console.error("create-donation error:", error);
    return new Response(JSON.stringify({ error: "Unable to process donation. Please try again later." }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 500,
    });
  }
});
