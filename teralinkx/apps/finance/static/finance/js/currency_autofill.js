document.addEventListener('DOMContentLoaded', function() {
    // Wait for Django jQuery to be available
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        console.log('Waiting for Django jQuery...');
        setTimeout(function() {
            initCurrencyAutofill();
        }, 100);
    } else {
        initCurrencyAutofill();
    }
});

function initCurrencyAutofill() {
    var $ = django.jQuery;
    
    console.log('Initializing currency autofill...');
    
    // Get the code field
    var $codeField = $('#id_code');
    var $nameField = $('#id_name');
    var $symbolField = $('#id_symbol');
    var $unicodeField = $('#id_unicode_symbol');
    var $decimalField = $('#id_decimal_places');
    var $cryptoField = $('#id_is_crypto');
    
    // Check if we're on an add page and fields exist
    if ($codeField.length && $nameField.length && (!$nameField.val() || $nameField.val() === '')) {
        console.log('Setting up currency autofill...');
        
        $codeField.on('change', function() {
            var code = $(this).val();
            console.log('Currency code changed to:', code);
            
            if (code) {
                // Get the display name from the selected option
                var $option = $codeField.find('option:selected');
                var displayName = $option.text().split(' - ')[1] || $option.text(); // Get just the name part
                
                console.log('Display name:', displayName);
                
                // Auto-fill name from selected option text if empty
                if (!$nameField.val() || $nameField.val() === '') {
                    $nameField.val(displayName.trim());
                }
                
                // Get currency data from our mapping (client-side first)
                var currencyData = getCurrencyData(code);
                
                // Only auto-fill if fields are empty
                if (!$symbolField.val() || $symbolField.val() === '') {
                    $symbolField.val(currencyData.symbol);
                }
                
                if (!$unicodeField.val() || $unicodeField.val() === '') {
                    $unicodeField.val(currencyData.unicode_symbol);
                }
                
                if (!$decimalField.val() || $decimalField.val() === '2' || $decimalField.val() === '') {
                    $decimalField.val(currencyData.decimal_places);
                }
                
                // Set crypto flag
                if (currencyData.is_crypto) {
                    $cryptoField.prop('checked', true);
                }
            }
        });
        
        // Also trigger on page load if code is already selected
        if ($codeField.val()) {
            $codeField.trigger('change');
        }
    }
}

// Client-side currency data mapping (fallback if server API fails)
function getCurrencyData(code) {
    var currencyData = {
        'KES': {name: 'Kenyan Shilling', symbol: 'KSh', unicode_symbol: 'KSh', decimal_places: 2, is_crypto: false},
        'USD': {name: 'US Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'EUR': {name: 'Euro', symbol: '€', unicode_symbol: '€', decimal_places: 2, is_crypto: false},
        'GBP': {name: 'British Pound', symbol: '£', unicode_symbol: '£', decimal_places: 2, is_crypto: false},
        'ZAR': {name: 'South African Rand', symbol: 'R', unicode_symbol: 'R', decimal_places: 2, is_crypto: false},
        'AED': {name: 'UAE Dirham', symbol: 'د.إ', unicode_symbol: 'د.إ', decimal_places: 2, is_crypto: false},
        'JPY': {name: 'Japanese Yen', symbol: '¥', unicode_symbol: '¥', decimal_places: 0, is_crypto: false},
        'CNY': {name: 'Chinese Yuan', symbol: '¥', unicode_symbol: '¥', decimal_places: 2, is_crypto: false},
        'INR': {name: 'Indian Rupee', symbol: '₹', unicode_symbol: '₹', decimal_places: 2, is_crypto: false},
        'BTC': {name: 'Bitcoin', symbol: '₿', unicode_symbol: '₿', decimal_places: 8, is_crypto: true},
        'ETH': {name: 'Ethereum', symbol: 'Ξ', unicode_symbol: 'Ξ', decimal_places: 18, is_crypto: true},
        'CAD': {name: 'Canadian Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'CHF': {name: 'Swiss Franc', symbol: 'CHF', unicode_symbol: 'CHF', decimal_places: 2, is_crypto: false},
        'AUD': {name: 'Australian Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'NZD': {name: 'New Zealand Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'SGD': {name: 'Singapore Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'HKD': {name: 'Hong Kong Dollar', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'SEK': {name: 'Swedish Krona', symbol: 'kr', unicode_symbol: 'kr', decimal_places: 2, is_crypto: false},
        'NOK': {name: 'Norwegian Krone', symbol: 'kr', unicode_symbol: 'kr', decimal_places: 2, is_crypto: false},
        'DKK': {name: 'Danish Krone', symbol: 'kr', unicode_symbol: 'kr', decimal_places: 2, is_crypto: false},
        'PLN': {name: 'Polish Złoty', symbol: 'zł', unicode_symbol: 'zł', decimal_places: 2, is_crypto: false},
        'TRY': {name: 'Turkish Lira', symbol: '₺', unicode_symbol: '₺', decimal_places: 2, is_crypto: false},
        'RUB': {name: 'Russian Ruble', symbol: '₽', unicode_symbol: '₽', decimal_places: 2, is_crypto: false},
        'BRL': {name: 'Brazilian Real', symbol: 'R$', unicode_symbol: 'R$', decimal_places: 2, is_crypto: false},
        'MXN': {name: 'Mexican Peso', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'ARS': {name: 'Argentine Peso', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'CLP': {name: 'Chilean Peso', symbol: '$', unicode_symbol: '$', decimal_places: 0, is_crypto: false},
        'COP': {name: 'Colombian Peso', symbol: '$', unicode_symbol: '$', decimal_places: 2, is_crypto: false},
        'PEN': {name: 'Peruvian Sol', symbol: 'S/', unicode_symbol: 'S/', decimal_places: 2, is_crypto: false},
        'EGP': {name: 'Egyptian Pound', symbol: '£', unicode_symbol: '£', decimal_places: 2, is_crypto: false},
        'NGN': {name: 'Nigerian Naira', symbol: '₦', unicode_symbol: '₦', decimal_places: 2, is_crypto: false},
        'GHS': {name: 'Ghanaian Cedi', symbol: '₵', unicode_symbol: '₵', decimal_places: 2, is_crypto: false},
        'MAD': {name: 'Moroccan Dirham', symbol: 'د.م.', unicode_symbol: 'د.م.', decimal_places: 2, is_crypto: false},
        'THB': {name: 'Thai Baht', symbol: '฿', unicode_symbol: '฿', decimal_places: 2, is_crypto: false},
        'IDR': {name: 'Indonesian Rupiah', symbol: 'Rp', unicode_symbol: 'Rp', decimal_places: 2, is_crypto: false},
        'MYR': {name: 'Malaysian Ringgit', symbol: 'RM', unicode_symbol: 'RM', decimal_places: 2, is_crypto: false},
        'PHP': {name: 'Philippine Peso', symbol: '₱', unicode_symbol: '₱', decimal_places: 2, is_crypto: false},
        'VND': {name: 'Vietnamese Đồng', symbol: '₫', unicode_symbol: '₫', decimal_places: 0, is_crypto: false},
        'KRW': {name: 'South Korean Won', symbol: '₩', unicode_symbol: '₩', decimal_places: 0, is_crypto: false},
        'ILS': {name: 'Israeli New Shekel', symbol: '₪', unicode_symbol: '₪', decimal_places: 2, is_crypto: false}
    };
    
    return currencyData[code] || {
        name: code,
        symbol: code,
        unicode_symbol: code,
        decimal_places: 2,
        is_crypto: false
    };
}