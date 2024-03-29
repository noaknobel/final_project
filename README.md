# Excel-Like Spreadsheet Application

## Overview

This project delivers an advanced spreadsheet application mirroring Excel's capabilities, tailored for both personal and professional environments. It facilitates efficient data management, complex calculations, and in-depth analysis with its user-friendly interface, supporting an extensive array of mathematical and logical operations for enhanced productivity.

## Key Expansions

- **Graphical User Interface (GUI):** A sophisticated GUI ensures seamless user interaction, featuring intuitive navigation, cell selection, and formula input. The design principles prioritize modularity and a clear division of responsibilities between the Sheet class (backend) and the Sheet Visualizer (frontend), enhancing maintainability and user experience.

- **Advanced Formulas:**
  - Implementation of advanced mathematical functions such as sinusoidal and exponential calculations.
  - Incorporation of associativity and precedence rules inspired by the Shunting Yard algorithm.
  - Capability to assign and interpret string values within calculations.

- **Data Export:** Provides functionality to export spreadsheet data into CSV format, facilitating data sharing and analysis outside the application.

- **Type Annotations:** Utilization of type annotations throughout the codebase to improve readability, facilitate debugging, and support static code analysis tools.

## Sophisticated Programming Techniques

- **Robust Error Handling:** Employs comprehensive error handling mechanisms across formula parsing, circular reference detection, and execution processes, ensuring high data integrity. The backend leverages an Enum of FailureReasons, while the frontend utilizes message boxes to provide detailed error feedback to the user.

- **Innovative Data Structures:**
  - Utilizes graphs to efficiently manage cell dependencies, ensuring accurate calculation results.
  - Employs dictionaries to represent cells, optimizing memory usage without compromising functionality.
  - Adopts a Node (tree) structure to facilitate the handling of complex formulas.
  - Incorporates stacks to aid in the parsing and evaluation of formulas, enhancing performance and reliability.

- **Advanced Programming Features:** Demonstrates the use of sophisticated programming constructs. These include lambda expressions, showcasing concise and functional approaches to problem-solving. Inheritance models are utilized to promote code reuse and polymorphism. Regular expressions facilitate pattern matching and data validation, ensuring robust input handling. Generator functions (`yield from`) are employed for efficient data processing. Enums are used to define a set of named constants, providing clarity and reducing errors in code.

- **Expansion Potential:** The current GUI supports a fixed grid size, yet the backend architecture is designed to theoretically accommodate an unlimited range of cells, offering significant potential for future scalability and feature development.
