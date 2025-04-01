"use client"


import React, { useState, useRef } from "react";
import './Navbar.css';
import "./first-level-filter.css";
import emailjs from "@emailjs/browser";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiscord, faGithub, faLinkedin, faInstagram, faYoutube } from "@fortawesome/free-brands-svg-icons";
import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import Link from 'next/link'



const contactPage = () => {

  const form = useRef();
  const [status, setStatus] = useState("");

  const sendEmail = async (e) => {
    e.preventDefault();
    setStatus("Sending..."); 

    emailjs.init("your_correct_public_key"); 

    try {
      const result = await emailjs.sendForm(
        "service_4rpjqlh",  
        "template_9ywy7aw", 
        form.current,
        "hIojCZUZcoXSb386o"
      );

      console.log("Email Sent Successfully:", result);
      setStatus("Message sent successfully!");
      form.current.reset(); 

    } catch (error) {
      console.error("EmailJS Error:", error);
      setStatus(`Failed to send message: ${error.text || "Unknown error"}`);
    }
  };

  return (

    <>

      <div className="bg-white min-h-screen flex flex-col items-center p-6">
        {/* Navbar */}
        <nav className="navbar py-4 ">
              <Link href="/" className="logo cursor-pointer flex items-center">
                <span className="bold">Vike</span>
                <span>Eats</span>
              </Link>
              <div className="nav-links">
                  <ul>
                      <li><a href="#">Food Establishments</a></li>
                      <li><a href="#">Amenities</a></li>
                      <li><Link href="/contact">Contact Us</Link></li>
                  </ul>
              </div>
          </nav>


        <div className="text-primary-dark w-full flex justify-center items-center mt-14 pt-9">
          <h2 className="text-3xl font-semibold text-center">Contact Us</h2>
        </div>



        <div className="max-w-[100%] w-full flex flex-col lg:flex-row justify-between items-start gap-12 mt-12 px-6 lg:px-20 pb-20">
          {/* Left Section: Info */}
          <div className="text-primary-dark w-full lg:w-3/5 bg-white p-16 rounded-lg lg:min-h-[700px] py-18 sm:shadow-dark sm:shadow-gray-200 lg:shadow-none">

            {/* About VikeLabs */}
            <section className="mt-2">
              <h3 className="text-xl font-bold">What is VikeLabs?</h3>

              <p className="mt-2 text-primary-dark pt-4">
                VikeLabs is a collective of students who learn to build, deploy, and test software apps. We are a community of student developers, designers, and entrepreneurs who are passionate about designing software solutions for students and the UVic campus community.
              </p>

              <div className="py-5 ">
              <a
                href="https://discord.gg/p8yrwrrSWw"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block"
              >
                <button className="text-primary-dark mt-4 bg-gray-200 p-3 rounded-lg flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                  <FontAwesomeIcon icon={faDiscord} className="text-xl" />
                  Join Our Discord!
                </button>

              </a>

              </div>

            </section>

            <hr className="my-6" />

            {/* About VikeEats */}
            <section className="text-primary-dark">
              <h3 className="text-xl font-bold pt-5">What is VikeEats?</h3>
              <p className="text-primary-dark mt-2 pt-4">
                VikeEats is a University of Victoria project that offers an interactive map of campus dining options, including cafeterias and restaurants. It highlights the sorts of foods offered at each restaurant, such as gluten-free, dairy-free, vegetarian, and vegan alternatives, allowing students and guests to make more educated dining choices.
              </p>
              <div className="flex py-5 justify-start gap-4">
                
                <a href="mailto:vikelab@gmail.com" className="inline-block">
                  <button className="text-primary-dark mt-4 bg-gray-200 p-3 flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out rounded-3xl">
                    <FontAwesomeIcon icon={faEnvelope} className="text-xl" />
                  </button>
                </a>
                
                <a
                  href="https://github.com/VikeLabs/VikeEats"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <button className="text-primary-dark mt-4 bg-gray-200 p-3 rounded-3xl flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                  <FontAwesomeIcon icon={faGithub} className="text-xl" />

                  </button>

                </a>
                
                <a
                  href="https://www.linkedin.com/company/vikelabs/?originalSubdomain=ca"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <button className="text-primary-dark mt-4 bg-gray-200 p-3 rounded-3xl flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                  <FontAwesomeIcon icon={faLinkedin} className="text-xl" />

                  </button>

                </a>
                
                <a
                  href="https://www.instagram.com/vikelabs/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <button className="text-primary-dark mt-4 bg-gray-200 p-3 rounded-3xl flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                  <FontAwesomeIcon icon={faInstagram} className="text-xl" />
                  </button>
                </a>

                <a
                  href="https://www.youtube.com/channel/UCKAAXo4bqb034PZYR6ZhpQw"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <button className="text-primary-dark mt-4 bg-gray-200 p-3 rounded-3xl flex items-center gap-2 hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                  <FontAwesomeIcon icon={faYoutube} className="text-xl" /></button>
                </a>
                
              </div>

            </section>
          </div>

          {/* Right Section: Contact Form */}
          <div className="text-primary-dark w-full lg:w-2/5 bg-white p-10 lg:p-12 rounded-lg shadow-dark shadow-gray-200 flex flex-col justify-between lg:min-h-[700px]">
            <form ref={form} onSubmit={sendEmail} className="flex flex-col flex-grow">
              
              <label className="block font-semibold">Name</label>
              <input type="text" name="name" className="w-full p-3 border rounded mt-1" placeholder="Enter your name" required />

              <label className="block font-semibold mt-4">Surname</label>
              <input type="text" name="surname" className="w-full p-3 border rounded mt-1" placeholder="Enter your surname" required />

              <label className="block font-semibold mt-4">Email</label>
              <input type="email" name="email" className="w-full p-3 border rounded mt-1" placeholder="Enter your email" required />

              <label className="block font-semibold mt-4">Message</label>
              <textarea name="message" className="w-full p-3 border rounded mt-1 flex-grow min-h-[200px]" placeholder="Enter your message" required></textarea>

              <button type="submit" className="w-full bg-gray-900 text-white p-3 mt-4 rounded hover:bg-primary-light hover:text-white transition duration-300 ease-in-out">
                Submit
              </button>

              {status && <p className="mt-4 text-sm text-gray-700">{status}</p>}
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default contactPage;



