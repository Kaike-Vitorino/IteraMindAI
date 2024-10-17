# Contributing to IteraMindAI

Thank you for considering contributing to **IteraMindAI**! We welcome contributions from the community, whether you are fixing bugs, adding new features, improving documentation, or providing feedback. Please follow the guidelines below to ensure a smooth collaboration.


## **How to Contribute**
1. **Fork the Repository**:
   - Create a personal copy of this repository by clicking the "Fork" button on GitHub.

2. **Clone Your Fork**:
   - Clone your forked repository to your local machine:
     ```bash
     git clone https://github.com/your-username/IteraMindAI.git
     cd IteraMindAI
     ```

3. **Create a New Branch**:
   - Use a separate branch for each contribution to keep changes organized:
     ```bash
     git checkout -b feature/your-feature-name
     ```

4. **Install Dependencies**:
   - Ensure that all environments are properly configured (refer to the README for setup instructions).

5. **Make Your Changes**:
   - Ensure your code follows the project’s coding standards and is properly documented.

6. **Run Tests**:
   - Make sure your changes pass all existing tests:
     ```bash
     # Rust
     cd core-rust && cargo test

     # Go
     cd backend-go && go test ./...

     # Python
     cd integration-python && pytest
     ```

7. **Commit Your Changes**:
   - Write meaningful commit messages that explain your changes:
     ```bash
     git add .
     git commit -m "Add: Detailed description of your changes"
     ```

8. **Push Your Changes**:
   - Push your branch to your forked repository:
     ```bash
     git push origin feature/your-feature-name
     ```

9. **Submit a Pull Request**:
   - Open a Pull Request on the original repository, describing your changes and why they should be merged.

---

## **Code of Conduct**
Please ensure all interactions follow the **Code of Conduct**:
- Be respectful and considerate of others' contributions.
- Avoid inflammatory language or personal attacks.
- Provide constructive feedback when reviewing code.

---

## **Issue Reporting and Suggestions**
- Found a bug? Open an issue with a clear description and steps to reproduce it.
- Have a feature request? Submit it as an issue and provide as much detail as possible.

---

## **Getting Help**
If you have any questions or need help, feel free to:
- Join our community on **Discord/Slack** (if available).
- Reach out via **email**: your-email@example.com.

We appreciate your contributions and efforts to improve IteraMindAI!
