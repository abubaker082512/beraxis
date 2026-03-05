import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter, CardDescription } from '@/components/ui/Card';
import { Check, Zap, Star, Shield } from 'lucide-react';

export default function Pricing() {
  const [isYearly, setIsYearly] = React.useState(false);

  const plans = [
    {
      name: "Starter",
      price: isYearly ? 49 : 59,
      description: "Perfect for small businesses starting with AI calling.",
      features: [
        "Up to 500 minutes/mo",
        "2 AI Agents",
        "Standard Voices",
        "Basic Analytics",
        "Email Support"
      ],
      buttonText: "Start Free Trial",
      highlight: false
    },
    {
      name: "Professional",
      price: isYearly ? 149 : 179,
      description: "Ideal for growing teams with higher call volume.",
      features: [
        "Up to 2,500 minutes/mo",
        "10 AI Agents",
        "Premium Voices",
        "Advanced Analytics",
        "Priority Support",
        "CRM Integrations"
      ],
      buttonText: "Get Started",
      highlight: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large scale operations with custom requirements.",
      features: [
        "Unlimited minutes",
        "Unlimited AI Agents",
        "Custom Voice Cloning",
        "Dedicated Account Manager",
        "SLA Guarantee",
        "On-premise Deployment"
      ],
      buttonText: "Contact Sales",
      highlight: false
    }
  ];

  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-bold font-display mb-6"
          >
            Simple, Transparent <span className="text-primary">Pricing</span>
          </motion.h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Choose the plan that's right for your business. No hidden fees.
          </p>

          {/* Toggle */}
          <div className="flex items-center justify-center space-x-4">
            <span className={!isYearly ? "text-foreground font-medium" : "text-muted-foreground"}>Monthly</span>
            <button 
              onClick={() => setIsYearly(!isYearly)}
              className="w-14 h-7 bg-muted rounded-full p-1 relative transition-colors hover:bg-muted/80"
            >
              <motion.div 
                animate={{ x: isYearly ? 28 : 0 }}
                className="w-5 h-5 bg-primary rounded-full shadow-lg"
              />
            </button>
            <span className={isYearly ? "text-foreground font-medium" : "text-muted-foreground"}>
              Yearly <span className="text-primary text-xs font-bold ml-1">SAVE 20%</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className={`h-full relative flex flex-col ${plan.highlight ? 'border-primary neon-border scale-105 z-10' : 'border-border'}`}>
                {plan.highlight && (
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-black text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                    Most Popular
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4 flex items-baseline">
                    <span className="text-4xl font-bold font-display">
                      {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                    </span>
                    {typeof plan.price === 'number' && (
                      <span className="ml-1 text-muted-foreground">/mo</span>
                    )}
                  </div>
                  <CardDescription className="mt-2">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-4">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-center space-x-3 text-sm">
                        <Check className="text-primary w-4 h-4 shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button 
                    variant={plan.highlight ? "primary" : "outline"} 
                    className="w-full py-6 text-lg"
                  >
                    {plan.buttonText}
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* FAQ Preview */}
        <div className="mt-32 text-center">
          <h2 className="text-3xl font-bold font-display mb-12">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left max-w-4xl mx-auto">
            <div>
              <h4 className="font-bold mb-2">Can I cancel anytime?</h4>
              <p className="text-muted-foreground text-sm">Yes, you can cancel your subscription at any time. You'll have access until the end of your billing period.</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">What counts as a minute?</h4>
              <p className="text-muted-foreground text-sm">Any time an AI agent is actively connected to a call counts towards your monthly minute allowance.</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">Do you offer custom voices?</h4>
              <p className="text-muted-foreground text-sm">Yes, our Enterprise plan includes custom voice cloning to match your brand's specific tone.</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">Is there a setup fee?</h4>
              <p className="text-muted-foreground text-sm">No, there are no setup fees for our self-service plans. Enterprise setup may vary.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
