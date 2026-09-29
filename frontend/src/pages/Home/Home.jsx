import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import Features from "../../components/Features/Features";
import HowItWorks from "../../components/HowItWorks/HowItWorks";
import CTA from "../../components/CTA/CTA";
import Footer from "../../components/Footer/Footer";

function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <CTA />
      <Footer />
    </>
  );
}

export default Home;