// services/jwt.js
export const jwtService = {
  decode(token) {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('Failed to decode JWT:', error)
      return null
    }
  },

  getExpiry(token) {
    const decoded = this.decode(token)
    if (!decoded || !decoded.exp) return null
    return decoded.exp * 1000 // Convert to milliseconds
  },

  isExpired(token) {
    const expiry = this.getExpiry(token)
    if (!expiry) return true
    return Date.now() >= expiry
  },

  isValid(token) {
    return token && !this.isExpired(token)
  },

  getClaim(token, claim) {
    const decoded = this.decode(token)
    return decoded ? decoded[claim] : null
  },

  // Get all required payment claims
  getPaymentClaims(token) {
    const decoded = this.decode(token)
    if (!decoded) return null
    
    return {
      client_account: decoded.client_account,
      account_tier: decoded.account_tier,
      balance: decoded.balance,
      phone_number: decoded.phone_number,
      location_id: decoded.location_id || decoded.current_location_id,
      is_active: decoded.is_active,
      auto_renew: decoded.auto_renew,
      two_factor_enabled: decoded.two_factor_enabled,
      active_voucher: decoded.active_voucher,
      voucher_expires_at: decoded.voucher_expires_at
    }
  },

  // Verify token has all required claims for payment system
  hasRequiredClaims(token) {
    const requiredClaims = [
      'client_account',
      'account_tier',
      'balance',
      'phone_number',
      'location_id'
    ]
    
    const decoded = this.decode(token)
    if (!decoded) return false
    
    return requiredClaims.every(claim => 
      decoded[claim] !== undefined && decoded[claim] !== null
    )
  }
}