# Modern Mortgage Calculator

A completely redesigned and enhanced version of the [original mortgage calculator project](https://github.com/JiteshKumar53/Project--Mortgage-Calculator-.git) with significant improvements in functionality, user interface, and code architecture.

## 🚀 Key Improvements Over Original Version

### User Interface Enhancements
- Modern, clean interface with Tailwind-inspired styling
- Two-column layout for better organization of information
- Interactive tooltips for better user guidance
- Real-time updates for down payment and loan amount calculations
- Keyboard shortcuts for common actions (Ctrl+Enter, Ctrl+C, Ctrl+E)

### New Features
- Auto/Manual down payment mode with 15% default calculation
- Support for multiple currencies (SEK, USD, EUR, CAD, AUD, INR, JPY, GBP)
- Monthly house fee consideration in calculations
- Enhanced visualization with yearly payment breakdown
- Detailed PDF export with comprehensive loan information
- Export directory management for organizing generated PDFs

### Technical Improvements
- Object-oriented architecture with clear separation of concerns
- Robust input validation with meaningful error messages
- Enhanced error handling throughout the application
- Modular code structure for better maintainability
- Automated calculation of loan terms and payoff time
- Dynamic plot sizing and formatting

## 📊 Feature Comparison

| Feature | Original Version | New Version |
|---------|-----------------|-------------|
| UI Design | Basic Tkinter | Modern with ttkbootstrap |
| Currency Support | Single (SEK) | Multiple (8 currencies) |
| Down Payment | Manual only | Auto/Manual with 15% default |
| Visualization | None | Interactive yearly breakdown |
| PDF Export | Basic | Comprehensive with plots |
| Error Handling | Basic | Robust with user feedback |
| Code Architecture | Procedural | Object-oriented |
| Input Validation | Basic | Comprehensive |
| Extra Features | None | House fees, tooltips, shortcuts |

## 🖥️ Usage Instructions

1. Launch the application:
   ```bash
   python mortgage_calculator_new.py
   ```

2. Select your preferred currency from the dropdown menu

3. Enter loan details:
   - Loan seeking amount
   - Choose auto/manual down payment mode
   - Interest rate (default 4.5%)
   - Principal payment
   - Optional: extra payment and monthly house fee

4. Use keyboard shortcuts:
   - `Ctrl+Enter`: Calculate
   - `Ctrl+C`: Clear fields
   - `Ctrl+E`: Export to PDF
   - `Esc`: Exit application

5. View results in the right panel:
   - Monthly payment breakdown
   - Total interest calculations
   - Payment timeline
   - Visual yearly payment breakdown

6. Export detailed PDF reports with:
   - Complete loan details
   - Payment breakdowns
   - Visualization graphs
   - Export timestamp and calculations

## 💡 Additional Features

- **Auto-calculating Down Payment**: Automatically calculates 15% down payment in auto mode
- **Real-time Updates**: Instantly updates loan amount based on down payment changes
- **Currency Formatting**: Proper formatting for different currency types
- **Data Validation**: Prevents invalid inputs with helpful error messages
- **Export Management**: Organizes PDFs with timestamped filenames
- **Responsive Layout**: Adapts to different window sizes
- **Professional Reporting**: Generates detailed PDF reports with custom formatting

## 🛠️ Technical Requirements

- Python 3.x
- Required packages:
  - tkinter
  - ttkbootstrap
  - reportlab
  - matplotlib
  - numpy

## 📈 Performance Improvements

- Faster calculations with optimized algorithms
- Reduced memory usage through better resource management
- Smoother UI interactions with improved event handling
- Efficient PDF generation with optimized plot rendering
- Better file handling with organized export structure

This new version represents a significant upgrade in terms of functionality, user experience, and code quality, making it a more professional and user-friendly tool for mortgage calculations.