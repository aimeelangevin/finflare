import './App.css'
import React, { useState, useEffect } from 'react'

// CSRF Token Retrieval
function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

// Step 1: Profile Info
function Step1Profile({ formData, setFormData, nextStep }) {
    const [ageError, setAgeError] = useState('');
    
    const validateAge = () => {
        const age = parseInt(formData.age);
        
        if (!formData.age) {
            setAgeError('Age is required');
            return false;
        }
        
        if (isNaN(age)) {
            setAgeError('Please enter a valid number');
            return false;
        }
        
        if (age < 16) {
            setAgeError('You must be at least 16 years old');
            return false;
        }
        
        if (age > 100) {
            setAgeError('Please enter a valid age (between 16 and 100)');
            return false;
        }
        
        setAgeError('');
        return true;
    };
    
    const handleNext = () => {
        if (validateAge()) {
            nextStep();
        }
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">Tell us about you!</h3>
            <div className="space-y-4">
                <div>
                    <label htmlFor="age" className="block text-gray-700 mb-2">Age</label>
                    <input
                        id="age"
                        type="number"
                        name="age"
                        value={formData.age}
                        onChange={(e) => {
                            setFormData({ ...formData, age: e.target.value });
                            setAgeError(''); // Clear error when user types
                        }}
                        className={`input-field ${ageError ? 'border-red-500' : ''}`}
                        min="16"
                        max="100"
                        placeholder="Must be between 16 and 100"
                    />
                    {ageError && <p className="text-red-500 text-sm mt-1">{ageError}</p>}
                </div>
                <button 
                    onClick={handleNext}
                    className="btn-primary w-full"
                >
                    Next
                </button>
            </div>
        </div>
    )
}

// Step 2: Income & Employment
function Step2Employment({ formData, setFormData, nextStep, prevStep }) {
    const [employmentError, setEmploymentError] = useState('');
    const [incomeError, setIncomeError] = useState('');
    
    const validateEmployment = () => {
        const employment = formData.employment;
        
        if (!employment) {
            setEmploymentError('Employment is required');
            return false;
        }
        
        // Allow letters, spaces, apostrophes, hyphens, periods, ampersands, and commas
        const validEmploymentRegex = /^[a-zA-Z\s'\-\.&,]+$/;
        
        if (!validEmploymentRegex.test(employment)) {
            setEmploymentError('Please enter a valid employment');
            return false;
        }
        
        setEmploymentError('');
        return true;
    };
    
    const validateIncome = () => {
        const income = formData.income;
        
        if (!income) {
            setIncomeError('Income is required');
            return false;
        }
        
        // Remove dollar sign and commas for validation
        const numericIncome = income.replace(/[$,]/g, '');
        
        if (isNaN(numericIncome) || numericIncome <= 0) {
            setIncomeError('Please enter a valid income amount');
            return false;
        }
        
        setIncomeError('');
        return true;
    };
    
    const handleNext = () => {
        const isEmploymentValid = validateEmployment();
        const isIncomeValid = validateIncome();
        
        if (isEmploymentValid && isIncomeValid) {
            // Ensure retirement_date is properly set before proceeding
            if (formData.retirement_date === '') {
                // If checkbox is checked, keep it as empty string
                setFormData({ ...formData, retirement_date: '' });
            } else if (formData.retirement_date === null) {
                // If checkbox is unchecked and no date is selected, set to null
                setFormData({ ...formData, retirement_date: null });
            }
            // If a date is selected, keep it as is
            
            nextStep();
        }
    };
    
    const formatIncome = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with commas and dollar sign
        if (numericValue) {
            const formattedValue = parseInt(numericValue, 10).toLocaleString();
            return `${formattedValue}`;
        }
        
        return '';
    };
    
    const handleIncomeChange = (e) => {
        const value = e.target.value;
        
        // Remove dollar sign and commas for processing
        const numericValue = value.replace(/[$,]/g, '');
        
        // Update form data with the numeric value
        setFormData({ ...formData, income: numericValue });
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">Where do you work?</h3>
            <div className="space-y-4">
                <div>
                    <label htmlFor="employment" className="block text-gray-700 mb-2">Employment</label>
                    <input
                        id="employment"
                        type="text"
                        name="employment"
                        value={formData.employment}
                        onChange={(e) => {
                            setFormData({ ...formData, employment: e.target.value });
                            setEmploymentError(''); // Clear error when user types
                        }}
                        className={`input-field ${employmentError ? 'border-red-500' : ''}`}
                        placeholder="e.g. Software Engineer, Google or Google, Software Engineer"
                    />
                    <p className="text-gray-500 text-sm mt-1">Format: Role, Company or Company, Role</p>
                    {employmentError && <p className="text-red-500 text-sm mt-1">{employmentError}</p>}
                </div>
                <div>
                    <label htmlFor="income" className="block text-gray-700 mb-2">Income</label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                        <input
                            id="income"
                            type="text"
                            name="income"
                            value={formData.income ? formatIncome(formData.income) : ''}
                            onChange={handleIncomeChange}
                            className={`input-field pl-8 ${incomeError ? 'border-red-500' : ''}`}
                            placeholder="0"
                        />
                    </div>
                    {incomeError && <p className="text-red-500 text-sm mt-1">{incomeError}</p>}
                </div>
                <div>
                    <label htmlFor="retirement_date" className="block text-gray-700 mb-2">Retirement Date</label>
                    <div className="space-y-2">
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="retirement_date_unknown"
                                checked={formData.retirement_date === ''}
                                onChange={(e) => setFormData({ 
                                    ...formData, 
                                    retirement_date: e.target.checked ? '' : null 
                                })}
                                className="mr-2"
                            />
                            <label htmlFor="retirement_date_unknown" className="text-gray-700">I don't know my retirement date</label>
                        </div>
                        <input
                            id="retirement_date"
                            type="date"
                            name="retirement_date"
                            value={formData.retirement_date === null ? '' : formData.retirement_date}
                            onChange={(e) => setFormData({ ...formData, retirement_date: e.target.value })}
                            className="input-field"
                            disabled={formData.retirement_date === ''}
                        />
                    </div>
                </div>
                <div className="flex space-x-4">
                    <button 
                        onClick={prevStep}
                        className="btn-secondary flex-1"
                    >
                        Back
                    </button>
                    <button 
                        onClick={handleNext}
                        className="btn-primary flex-1"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}

// Step 3: Savings
function Step3Savings({ formData, setFormData, prevStep, nextStep }) {
    const [savingsError, setSavingsError] = useState('');
    
    const validateSavings = () => {
        const savings = formData.savings;
        
        if (!savings) {
            setSavingsError('Savings amount is required');
            return false;
        }
        
        // Remove dollar sign and commas for validation
        const numericSavings = savings.replace(/[$,]/g, '');
        
        if (isNaN(numericSavings) || numericSavings < 0) {
            setSavingsError('Please enter a valid savings amount');
            return false;
        }
        
        setSavingsError('');
        return true;
    };
    
    const formatSavings = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with commas and dollar sign
        if (numericValue) {
            const formattedValue = parseInt(numericValue, 10).toLocaleString();
            return `${formattedValue}`;
        }
        
        return '';
    };
    
    const handleSavingsChange = (e) => {
        const value = e.target.value;
        
        // Remove dollar sign and commas for processing
        const numericValue = value.replace(/[$,]/g, '');
        
        // Update form data with the numeric value
        setFormData({ ...formData, savings: numericValue });
        setSavingsError(''); // Clear error when user types
    };
    
    const handleNext = () => {
        if (validateSavings()) {
            nextStep();
        }
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">How much do you have saved?</h3>
            <div className="space-y-4">
                <div>
                    <label htmlFor="savings" className="block text-gray-700 mb-2">Savings</label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                        <input
                            id="savings"
                            type="text"
                            name="savings"
                            value={formData.savings ? formatSavings(formData.savings) : ''}
                            onChange={handleSavingsChange}
                            className={`input-field pl-8 ${savingsError ? 'border-red-500' : ''}`}
                            placeholder="0"
                        />
                    </div>
                    {savingsError && <p className="text-red-500 text-sm mt-1">{savingsError}</p>}
                </div>
                <div className="flex space-x-4">
                    <button 
                        onClick={prevStep}
                        className="btn-secondary flex-1"
                    >
                        Back
                    </button>
                    <button 
                        onClick={handleNext}
                        className="btn-primary flex-1"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}

// Step 4: Bank
function Step4BankingInfo({ formData, setFormData, prevStep, nextStep }) {
    const [bankNameError, setBankNameError] = useState('');
    const [balanceError, setBalanceError] = useState('');
    
    const validateBankName = () => {
        const bankName = formData.bank_name;
        
        if (!bankName) {
            setBankNameError('Bank name is required');
            return false;
        }
        
        // Allow letters, spaces, apostrophes, hyphens, periods, and ampersands
        const validBankNameRegex = /^[a-zA-Z\s'\-\.&]+$/;
        
        if (!validBankNameRegex.test(bankName)) {
            setBankNameError('Please enter a valid bank name');
            return false;
        }
        
        setBankNameError('');
        return true;
    };
    
    const validateBalance = () => {
        const balance = formData.balance;
        
        if (!balance) {
            setBalanceError('Balance is required');
            return false;
        }
        
        // Remove dollar sign and commas for validation
        const numericBalance = balance.replace(/[$,]/g, '');
        
        if (isNaN(numericBalance) || numericBalance < 0) {
            setBalanceError('Please enter a valid balance amount');
            return false;
        }
        
        setBalanceError('');
        return true;
    };
    
    const formatBalance = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with commas and dollar sign
        if (numericValue) {
            const formattedValue = parseInt(numericValue, 10).toLocaleString();
            return `${formattedValue}`;
        }
        
        return '';
    };
    
    const handleBalanceChange = (e) => {
        const value = e.target.value;
        
        // Remove dollar sign and commas for processing
        const numericValue = value.replace(/[$,]/g, '');
        
        // Update form data with the numeric value
        setFormData({ ...formData, balance: numericValue });
        setBalanceError(''); // Clear error when user types
    };
    
    const handleNext = () => {
        const isBankNameValid = validateBankName();
        const isBalanceValid = validateBalance();
        
        if (isBankNameValid && isBalanceValid) {
            nextStep();
        }
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">Connect your bank</h3>
            <div className="space-y-4">
                <div>
                    <label htmlFor="bank_name" className="block text-gray-700 mb-2">Bank Name</label>
                    <input
                        id="bank_name"
                        type="text"
                        name="bank_name"
                        value={formData.bank_name}
                        onChange={(e) => {
                            setFormData({ ...formData, bank_name: e.target.value });
                            setBankNameError(''); // Clear error when user types
                        }}
                        className={`input-field ${bankNameError ? 'border-red-500' : ''}`}
                        placeholder="Enter your bank name"
                    />
                    {bankNameError && <p className="text-red-500 text-sm mt-1">{bankNameError}</p>}
                </div>
                <div>
                    <label htmlFor="account_number" className="block text-gray-700 mb-2">Account Number</label>
                    <input
                        id="account_number"
                        type="number"
                        name="account_number"
                        value={formData.account_number}
                        onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                        className="input-field"
                    />
                </div>
                <div>
                    <label htmlFor="balance" className="block text-gray-700 mb-2">Balance</label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                        <input
                            id="balance"
                            type="text"
                            name="balance"
                            value={formData.balance ? formatBalance(formData.balance) : ''}
                            onChange={handleBalanceChange}
                            className={`input-field pl-8 ${balanceError ? 'border-red-500' : ''}`}
                            placeholder="0"
                        />
                    </div>
                    {balanceError && <p className="text-red-500 text-sm mt-1">{balanceError}</p>}
                </div>
                <div className="flex space-x-4">
                    <button 
                        onClick={prevStep}
                        className="btn-secondary flex-1"
                    >
                        Back
                    </button>
                    <button 
                        onClick={handleNext}
                        className="btn-primary flex-1"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}

// Step 5: Goals
function Step5Goals({ formData, setFormData, prevStep, nextStep }) {
    const [priorityError, setPriorityError] = useState('');
    const [amtError, setAmtError] = useState('');
    
    const validatePriority = () => {
        const priority = formData.priority;
        
        // If priority is empty, that's fine since this step is optional
        if (!priority) {
            setPriorityError('');
            return true;
        }
        
        // Check if priority is a number between 1 and 5
        const priorityNum = parseInt(priority);
        if (isNaN(priorityNum) || priorityNum < 1 || priorityNum > 5) {
            setPriorityError('Priority must be a number between 1 and 5');
            return false;
        }
        
        setPriorityError('');
        return true;
    };
    
    const validateAmt = () => {
        const amt = formData.amt;
        
        // If amt is empty, that's fine since this step is optional
        if (!amt) {
            setAmtError('');
            return true;
        }
        
        // Remove dollar sign and commas for validation
        const numericAmt = amt.replace(/[$,]/g, '');
        
        if (isNaN(numericAmt) || numericAmt < 0) {
            setAmtError('Please enter a valid amount');
            return false;
        }
        
        setAmtError('');
        return true;
    };
    
    const formatAmt = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with commas and dollar sign
        if (numericValue) {
            const formattedValue = parseInt(numericValue, 10).toLocaleString();
            return `${formattedValue}`;
        }
        
        return '';
    };
    
    const handleAmtChange = (e) => {
        const value = e.target.value;
        
        // Remove dollar sign and commas for processing
        const numericValue = value.replace(/[$,]/g, '');
        
        // Update form data with the numeric value
        setFormData({ ...formData, amt: numericValue });
        setAmtError(''); // Clear error when user types
    };
    
    const handlePriorityChange = (e) => {
        const value = e.target.value;
        
        // Only allow numbers 1-5
        if (value === '' || /^[1-5]$/.test(value)) {
            setFormData({ ...formData, priority: value });
            setPriorityError(''); // Clear error when user types
        }
    };
    
    const handleNext = () => {
        const isPriorityValid = validatePriority();
        const isAmtValid = validateAmt();
        
        if (isPriorityValid && isAmtValid) {
            nextStep();
        }
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">Set your initial goal</h3>
            <h2 className="text-gray-500 mb-4">(Optional - You can skip this step)</h2>
            <div className="space-y-4">
                <div>
                    <label htmlFor="goal_name" className="block text-gray-700 mb-2">Goal Name</label>
                    <input
                        id="goal_name"
                        type="text"
                        name="goal_name"
                        value={formData.goal_name}
                        onChange={(e) => setFormData({ ...formData, goal_name: e.target.value })}
                        className="input-field"
                        placeholder="Enter your goal name"
                    />
                </div>
                <div>
                    <label htmlFor="type_of_goal" className="block text-gray-700 mb-2">Type of Goal</label>
                    <select
                        id="type_of_goal"
                        name="type_of_goal"
                        value={formData.type_of_goal}
                        onChange={(e) => setFormData({ ...formData, type_of_goal: e.target.value })}
                        className="input-field"
                    >
                        <option value="">Select a goal type</option>
                        <option value="save_money">Save Money</option>
                        <option value="buy_house">Buy a House</option>
                        <option value="pay_debt">Pay Off Debt</option>
                        <option value="emergency_fund">Emergency Fund</option>
                        <option value="not_set">None for now!</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="goal_date" className="block text-gray-700 mb-2">Goal Date</label>
                    <input
                        id="goal_date"
                        type="date"
                        name="goal_date"
                        value={formData.goal_date}
                        onChange={(e) => setFormData({ ...formData, goal_date: e.target.value })}
                        className="input-field"
                    />
                </div>
                <div>
                    <label htmlFor="priority" className="block text-gray-700 mb-2">Priority (1-5)</label>
                    <input
                        id="priority"
                        type="text"
                        name="priority"
                        value={formData.priority}
                        onChange={handlePriorityChange}
                        className={`input-field ${priorityError ? 'border-red-500' : ''}`}
                        placeholder="1-5"
                        maxLength="1"
                    />
                    {priorityError && <p className="text-red-500 text-sm mt-1">{priorityError}</p>}
                </div>
                <div>
                    <label htmlFor="amt" className="block text-gray-700 mb-2">Goal Amount</label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                        <input
                            id="amt"
                            type="text"
                            name="amt"
                            value={formData.amt ? formatAmt(formData.amt) : ''}
                            onChange={handleAmtChange}
                            className={`input-field pl-8 ${amtError ? 'border-red-500' : ''}`}
                            placeholder="0"
                        />
                    </div>
                    {amtError && <p className="text-red-500 text-sm mt-1">{amtError}</p>}
                </div>
                <div className="flex space-x-4">
                    <button 
                        onClick={prevStep}
                        className="btn-secondary flex-1"
                    >
                        Back
                    </button>
                    <button 
                        onClick={handleNext}
                        className="btn-primary flex-1"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}

// Step 6: Investments
function Step6Investments({ formData, setFormData, prevStep, submitData }) {
    const [userAmtError, setUserAmtError] = useState('');
    const [roiError, setRoiError] = useState('');
    const [growthRateError, setGrowthRateError] = useState('');
    
    const validateUserAmt = () => {
        const userAmt = formData.user_amt;
        
        // If userAmt is empty, that's fine since this step is optional
        if (!userAmt) {
            setUserAmtError('');
            return true;
        }
        
        // Remove dollar sign and commas for validation
        const numericUserAmt = userAmt.replace(/[$,]/g, '');
        
        if (isNaN(numericUserAmt) || numericUserAmt < 0) {
            setUserAmtError('Please enter a valid amount');
            return false;
        }
        
        setUserAmtError('');
        return true;
    };
    
    const validateRoi = () => {
        const roi = formData.roi;
        
        // If roi is empty, that's fine since this step is optional
        if (!roi) {
            setRoiError('');
            return true;
        }
        
        // Remove percentage sign for validation
        const numericRoi = roi.replace(/%/g, '');
        
        if (isNaN(numericRoi)) {
            setRoiError('ROI must be a valid number');
            return false;
        }
        
        setRoiError('');
        return true;
    };
    
    const validateGrowthRate = () => {
        const growthRate = formData.growth_rate;
        
        // If growthRate is empty, that's fine since this step is optional
        if (!growthRate) {
            setGrowthRateError('');
            return true;
        }
        
        // Remove percentage sign for validation
        const numericGrowthRate = growthRate.replace(/%/g, '');
        
        if (isNaN(numericGrowthRate)) {
            setGrowthRateError('Growth rate must be a valid number');
            return false;
        }
        
        setGrowthRateError('');
        return true;
    };
    
    const formatUserAmt = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with commas and dollar sign
        if (numericValue) {
            const formattedValue = parseInt(numericValue, 10).toLocaleString();
            return `${formattedValue}`;
        }
        
        return '';
    };
    
    const formatPercentage = (value) => {
        // Remove all non-numeric characters
        const numericValue = value.replace(/[^0-9]/g, '');
        
        // Format with percentage sign
        if (numericValue) {
            return `${numericValue}%`;
        }
        
        return '';
    };
    
    const handleUserAmtChange = (e) => {
        const value = e.target.value;
        
        // Remove dollar sign and commas for processing
        const numericValue = value.replace(/[$,]/g, '');
        
        // Update form data with the numeric value
        setFormData({ ...formData, user_amt: numericValue });
        setUserAmtError(''); // Clear error when user types
    };
    
    const handleRoiChange = (e) => {
        const value = e.target.value;
        
        // Remove percentage sign for processing
        const numericValue = value.replace(/%/g, '');
        
        // Allow any numeric value
        if (numericValue === '' || !isNaN(numericValue)) {
            setFormData({ ...formData, roi: numericValue });
            setRoiError(''); // Clear error when user types
        }
    };
    
    const handleGrowthRateChange = (e) => {
        const value = e.target.value;
        
        // Remove percentage sign for processing
        const numericValue = value.replace(/%/g, '');
        
        // Allow any numeric value
        if (numericValue === '' || !isNaN(numericValue)) {
            setFormData({ ...formData, growth_rate: numericValue });
            setGrowthRateError(''); // Clear error when user types
        }
    };
    
    const handleSubmit = () => {
        const isUserAmtValid = validateUserAmt();
        const isRoiValid = validateRoi();
        const isGrowthRateValid = validateGrowthRate();
        
        if (isUserAmtValid && isRoiValid && isGrowthRateValid) {
            submitData();
        }
    };
    
    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-2xl font-bold text-finflare-blue mb-6 font-monaco">Investment Information</h3>
            <h2 className="text-gray-500 mb-4">(Optional - You can skip this step)</h2>
            <div className="space-y-4">
                <div>
                    <label htmlFor="investment_type" className="block text-gray-700 mb-2">Investment Type</label>
                    <select
                        id="investment_type"
                        name="investment_type"
                        value={formData.investment_type}
                        onChange={(e) => setFormData({ ...formData, investment_type: e.target.value })}
                        className="input-field"
                    >
                        <option value="">Select an investment type</option>
                        <option value="stocks">Stocks</option>
                        <option value="bonds">Bonds</option>
                        <option value="mutual_funds">Mutual Funds</option>
                        <option value="real_estate">Real Estate</option>
                        <option value="crypto">Crypto</option>
                        <option value="etfs">ETFs</option>
                        <option value="not_set">None for now!</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="investment_name" className="block text-gray-700 mb-2">Name of Investment</label>
                    <input
                        id="investment_name"
                        type="text"
                        name="investment_name"
                        value={formData.investment_name}
                        onChange={(e) => setFormData({ ...formData, investment_name: e.target.value })}
                        className="input-field"
                        placeholder="Enter investment name"
                    />
                </div>
                <div>
                    <label htmlFor="user_amt" className="block text-gray-700 mb-2">Amount</label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                        <input
                            id="user_amt"
                            type="text"
                            name="user_amt"
                            value={formData.user_amt ? formatUserAmt(formData.user_amt) : ''}
                            onChange={handleUserAmtChange}
                            className={`input-field pl-8 ${userAmtError ? 'border-red-500' : ''}`}
                            placeholder="0"
                        />
                    </div>
                    {userAmtError && <p className="text-red-500 text-sm mt-1">{userAmtError}</p>}
                </div>
                <div>
                    <label htmlFor="roi" className="block text-gray-700 mb-2">ROI (%)</label>
                    <div className="relative">
                        <input
                            id="roi"
                            type="text"
                            name="roi"
                            value={formData.roi ? formatPercentage(formData.roi) : ''}
                            onChange={handleRoiChange}
                            className={`input-field pr-8 ${roiError ? 'border-red-500' : ''}`}
                            placeholder="0-100"
                        />
                        <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                    </div>
                    {roiError && <p className="text-red-500 text-sm mt-1">{roiError}</p>}
                </div>
                <div>
                    <label htmlFor="growth_rate" className="block text-gray-700 mb-2">Growth Rate (%)</label>
                    <div className="relative">
                        <input
                            id="growth_rate"
                            type="text"
                            name="growth_rate"
                            value={formData.growth_rate ? formatPercentage(formData.growth_rate) : ''}
                            onChange={handleGrowthRateChange}
                            className={`input-field pr-8 ${growthRateError ? 'border-red-500' : ''}`}
                            placeholder="0-100"
                        />
                        <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                    </div>
                    {growthRateError && <p className="text-red-500 text-sm mt-1">{growthRateError}</p>}
                </div>
                <div>
                    <label htmlFor="risk_level" className="block text-gray-700 mb-2">Risk Level</label>
                    <select
                        id="risk_level"
                        name="risk_level"
                        value={formData.risk_level}
                        onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
                        className="input-field"
                    >
                        <option value="">Select a risk level</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                    </select>
                </div>
                <div className="flex space-x-4">
                    <button 
                        onClick={prevStep}
                        className="btn-secondary flex-1"
                    >
                        Back
                    </button>
                    <button 
                        onClick={handleSubmit}
                        className="btn-primary flex-1"
                    >
                        Submit
                    </button>
                </div>
            </div>
        </div>
    )
}

// Main Onboarding Flow
function Onboarding() {
    const [step, setStep] = useState(1)
    const [formData, setFormData] = useState({
        name: '',
        age: '',
        income: '',
        employment: '',
        retirement_date: null,
        savings: '',
        bank_name: '',
        account_number: '',
        balance: '',
        goal_name: '',
        type_of_goal: '',
        goal_date: '',
        priority: '',
        amt: '',
        investment_type: '',
        investment_name: '',
        user_amt: '',
        roi: '',
        growth_rate: '',
        risk_level: ''
    })

    const nextStep = () => setStep(step + 1)
    const prevStep = () => setStep(step - 1)

    function submitData() {
        const csrfToken = getCSRFToken()
        const xhr = new XMLHttpRequest()
        xhr.open('POST', '/onboarding/', true)
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
        xhr.setRequestHeader('X-CSRFToken', csrfToken)
        
        xhr.onload = function() {
            if (xhr.status === 200 || xhr.status === 302) {
                // The server will handle the redirect
                window.location.href = xhr.getResponseHeader('Location') || '/dashboard/'
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.errors) {
                        // Handle validation errors
                        if (response.errors.age) {
                            setFormData(prev => ({ ...prev, ageError: response.errors.age }));
                            setStep(1); // Go back to step 1
                        }
                        // Add more error handling for other fields as needed
                    } else {
                        console.error('Error submitting data:', xhr.responseText);
                    }
                } catch (e) {
                    console.error('Error parsing response:', e);
                }
            }
        }

        // Convert formData to URL-encoded string
        const data = Object.entries(formData)
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join('&')

        xhr.send(`${data}&csrfmiddlewaretoken=${csrfToken}`)
    }

    return (
        <div>
            {step === 1 && <Step1Profile formData={formData} setFormData={setFormData} nextStep={nextStep} />}
            {step === 2 && <Step2Employment formData={formData} setFormData={setFormData} nextStep={nextStep} prevStep={prevStep} />}
            {step === 3 && <Step3Savings formData={formData} setFormData={setFormData} nextStep={nextStep} prevStep={prevStep} />}
            {step === 4 && <Step4BankingInfo formData={formData} setFormData={setFormData} nextStep={nextStep} prevStep={prevStep} />}
            {step === 5 && <Step5Goals formData={formData} setFormData={setFormData} nextStep={nextStep} prevStep={prevStep} />}
            {step === 6 && <Step6Investments formData={formData} setFormData={setFormData} prevStep={prevStep} submitData={submitData} />}
        </div>
    )
}

// App Component
function App() {
    return (
        <div>
            <Onboarding />
        </div>
    )
}

export default App
