# Steve Arce Homework

## 🏗️ Activity #1:

### Vibe Check #1

 - Testing the functionallity of the System promp and developer promp by checking a bad mood behabior.
 - Developer promp: `You are an annoyed, impatient assistant...`
 - System promp: `You are a grumpy AI assistant. You're not in the mood to be friendly...`

 #### Question #1 ❓
  - How are you feeling today? And could you summarize quantum physics in one sentence?"
 #### Aspect Tested 🔍
 - He answers in a bad mood and without any desire to summarize, proving that he receives the prompts correctly.

 #### System Performance***  ✅
 - Indeed, it receives the parameters correctly and responds as it should.

### Vibe Check #2

 - Testing the markdown rendering.

 #### Question #1 ❓
  - Can you explain what Object-Oriented Programming (OOP) is in Python, with examples?
 #### Aspect Tested 🔍
 - Validate whether the frontend correctly formats the markdown and code blocks received from the LLM

 #### Initial State***  ❌
 - The frontend did not rendered any markdown correctly

 #### Current System Performance***  ✅  
 - The frontend rendered the markdown, inline code, and code blocks correctly, with the ability to copy the entire response or copy code from blocks.



### Vibe Check #3

 - Testing the dark/light mode toggle functionality.

 #### Question #1 ❓  
  - Can the user successfully switch between dark and light mode using the toggle button?
 #### Aspect Tested 🔍  
  - Validate whether the UI correctly applies theme changes and persists the selected mode across components.

 #### Initial State*** ❌
  - The toggle button was present but did not visually update the theme or reverted to the default mode after clicking. 

 #### Current System Performance***  ✅
  - The toggle now reliably switches between dark and light themes, applies the correct styling across the app, and persists the setting after navigation or refresh. 


### Vibe Check #4

 - Testing the drag-and-drop image upload functionality.

 #### Question #1 ❓  
  - Can the user drag and drop images into the UI and have them properly recognized and handled?

 #### Aspect Tested 🔍  
  - Validate whether the frontend correctly detects dropped files and provides a responsive visual overlay during the interaction.

 #### Initial State***  ❌
  - The drag-and-drop feature was buggy: dropping an image caused an error, and no overlay or proper upload trigger was shown. 

 #### Current System Performance***  ✅
  - A full-screen overlay appears when an image is dragged in, and the image is correctly handled and uploaded upon drop. The interaction is smooth and visually clear. 


### Vibe Check #5

 - Testing the responsive design and usability on mobile devices.

 #### Question #1 ❓  
  - Does the UI display correctly on mobile screens, with clear button labels and an optimized layout?

 #### Aspect Tested 🔍  
  - Validate whether the design adapts properly to smaller screens and ensures clarity and usability of key elements.

 #### Initial State***  ❌
  - Poor mobile design: sidebar was visible on small screens, buttons were misaligned or unclear, making interaction confusing. 

 #### Current System Performance***  ✅
  - Responsive layout now adapts cleanly to mobile devices. Buttons are clearly labeled and centered, including the new "Retry with other model" button, improving both aesthetics and usability. 



### Vibe Check #6

- Testing math formula rendering.

#### Question #1 ❓  
- If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each are needed to get exactly 12 apples and 9 oranges?

#### Aspect Tested 🔍  
- Confirms whether math formulas are rendered properly in markdown.

#### Initial State ❌  
- Math formulas were displayed as raw text.

#### Current System Performance ✅  
- Math rendering works correctly using libraries like `remarkMath` and `rehypeKatex`.




# Discussion Question #1

## What are some limitations of vibe checking as an evaluation tool?

 - Personally, I think an obvious limitation would be that at the level of a real project, we can't solemnly trust these types of validations to go live. Because there may be many things we don't notice at first glance, or that we don't easily ask ourselves, whether related to security or user experience.

 - Vibe checking relies heavily on personal interpretation. What feels good to one developer might be unusable to another or a non-technical user.

 - Without automation or formal QA processes, it doesn't scale well and offers limited reliability for ensuring long-term system quality.

 - I do think that for initial application testing, quickly detecting and correcting obvious errors, above all, saves the entire application a lot of time. This is something I'll continue to use when debugging initial and visible errors.

 - But I prefer to learn and master React/Next.js to implement a good production system that I trust, not something that AI generated and fixed on its own. AI makes a lot of mistakes, including poor security, and sometimes writes very outdated code if we don't remember to include good context and up-to-date documentation.