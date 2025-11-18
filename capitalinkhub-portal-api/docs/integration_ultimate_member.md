# Ultimate Member Integration Guide

Guide for integrating the Portal API with WordPress and the Ultimate Member plugin.

## Overview

The Portal API is designed to be called from WordPress PHP backend code, **not** from the browser. This ensures API keys remain secure and provides better control over data flow.

## Prerequisites

- WordPress site with Ultimate Member plugin installed and configured
- Portal API deployed and accessible
- Generated Portal API key
- SSL/HTTPS enabled (recommended for production)

## Integration Strategy

### High-Level Flow

```
WordPress User Action
    ↓
Ultimate Member Hook Fires
    ↓
Custom PHP Code
    ↓
HTTP Request to Portal API (with API key)
    ↓
Portal API Response
    ↓
Store/Display in WordPress
```

## Step 1: Configuration

### 1.1 Add Portal API Settings to WordPress

Add these settings to your WordPress configuration (via wp-config.php or custom plugin settings):

```php
<?php
// Option 1: wp-config.php (recommended for security)
define('PORTAL_API_BASE_URL', 'https://portal-api.capitalinkhub.com');
define('PORTAL_API_KEY', 'your-secret-api-key-here');

// Option 2: Store in wp_options (with encryption recommended)
update_option('portal_api_base_url', 'https://portal-api.capitalinkhub.com');
update_option('portal_api_key', 'your-secret-api-key-here');
?>
```

**Security Note:** Never expose the API key to the browser or JavaScript.

### 1.2 Create Helper Functions

Create a custom plugin or add to functions.php:

```php
<?php
/**
 * Helper function to make Portal API requests
 *
 * @param string $endpoint API endpoint (e.g., '/api/v1/members/resolve')
 * @param string $method HTTP method (GET, POST, etc.)
 * @param array|null $data Request body data
 * @return array|null Response data or null on error
 */
function portal_api_request($endpoint, $method = 'GET', $data = null) {
    $api_key = defined('PORTAL_API_KEY') ? PORTAL_API_KEY : get_option('portal_api_key');
    $base_url = defined('PORTAL_API_BASE_URL') ? PORTAL_API_BASE_URL : get_option('portal_api_base_url');

    if (empty($api_key) || empty($base_url)) {
        error_log('Portal API: Missing API key or base URL configuration');
        return null;
    }

    $args = [
        'method' => $method,
        'headers' => [
            'X-API-Key' => $api_key,
            'Content-Type' => 'application/json',
        ],
        'timeout' => 30,
    ];

    if ($data && in_array($method, ['POST', 'PUT', 'PATCH'])) {
        $args['body'] = json_encode($data);
    }

    $url = rtrim($base_url, '/') . $endpoint;
    $response = wp_remote_request($url, $args);

    if (is_wp_error($response)) {
        error_log('Portal API error: ' . $response->get_error_message());
        return null;
    }

    $status_code = wp_remote_retrieve_response_code($response);

    if ($status_code >= 400) {
        $body = wp_remote_retrieve_body($response);
        error_log("Portal API error (HTTP $status_code): $body");
        return null;
    }

    return json_decode(wp_remote_retrieve_body($response), true);
}

/**
 * Get or resolve portal member ID for a WordPress user
 *
 * @param int $user_id WordPress user ID
 * @return int|null Portal member ID or null on error
 */
function get_portal_member_id($user_id) {
    // Check if already stored
    $member_id = get_user_meta($user_id, '_portal_member_id', true);

    if ($member_id) {
        return (int)$member_id;
    }

    // Resolve via API
    $user = get_userdata($user_id);
    if (!$user) {
        return null;
    }

    // Determine role from Ultimate Member
    $um_role = 'buyer'; // default
    if (function_exists('um_user')) {
        um_fetch_user($user_id);
        $um_roles = um_user('role');
        if (is_array($um_roles)) {
            $um_role = in_array('um_seller', $um_roles) ? 'seller' : 'buyer';
        } elseif ($um_roles === 'um_seller') {
            $um_role = 'seller';
        }
    }

    $data = [
        'um_user_id' => (string)$user_id,
        'email' => $user->user_email,
        'role' => $um_role,
        'first_name' => $user->first_name,
        'last_name' => $user->last_name,
    ];

    $response = portal_api_request('/api/v1/members/resolve', 'POST', $data);

    if ($response && isset($response['member_id'])) {
        // Cache member ID
        update_user_meta($user_id, '_portal_member_id', $response['member_id']);
        return (int)$response['member_id'];
    }

    return null;
}
?>
```

## Step 2: Hook Into Ultimate Member Events

### 2.1 After User Registration/Approval

```php
<?php
/**
 * Resolve member when user is approved in Ultimate Member
 */
add_action('um_after_user_is_approved', function($user_id) {
    $member_id = get_portal_member_id($user_id);

    if ($member_id) {
        error_log("Portal member resolved: WP User $user_id → Member $member_id");
    } else {
        error_log("Failed to resolve portal member for WP User $user_id");
    }
});
?>
```

### 2.2 After User Login

```php
<?php
/**
 * Ensure member mapping exists on login
 */
add_action('um_on_login_before_redirect', function($user_id) {
    // Ensure member mapping exists
    get_portal_member_id($user_id);
});
?>
```

### 2.3 Profile Update Sync (Optional)

```php
<?php
/**
 * Sync profile updates to Portal API/CRM
 * Note: Portal API doesn't currently have update endpoint,
 * but this hook is where you'd add it
 */
add_action('um_after_user_updated', function($user_id, $args) {
    // Future: sync updates to CRM via Portal API
    // Example: portal_api_request("/api/v1/members/$member_id/profile", 'PUT', $updates);
}, 10, 2);
?>
```

## Step 3: Display Listings on Member Dashboard

### 3.1 Create Listings Shortcode

```php
<?php
/**
 * Shortcode to display business listings
 * Usage: [portal_listings industry="Technology" limit="10"]
 */
function portal_listings_shortcode($atts) {
    $atts = shortcode_atts([
        'industry' => '',
        'region' => '',
        'limit' => 20,
        'page' => 1,
    ], $atts);

    $query_params = http_build_query(array_filter([
        'industry' => $atts['industry'],
        'region' => $atts['region'],
        'page_size' => $atts['limit'],
        'page' => $atts['page'],
    ]));

    $response = portal_api_request('/api/v1/listings?' . $query_params);

    if (!$response || !isset($response['items'])) {
        return '<p>Unable to load listings. Please try again later.</p>';
    }

    $listings = $response['items'];
    $pagination = $response['pagination'];

    ob_start();
    ?>
    <div class="portal-listings">
        <?php foreach ($listings as $listing): ?>
            <div class="portal-listing-card">
                <h3><?php echo esc_html($listing['title']); ?></h3>
                <p class="listing-meta">
                    <strong>Industry:</strong> <?php echo esc_html($listing['industry'] ?? 'N/A'); ?> |
                    <strong>Region:</strong> <?php echo esc_html($listing['region'] ?? 'N/A'); ?> |
                    <strong>Revenue:</strong> <?php echo esc_html($listing['revenue_range'] ?? 'N/A'); ?>
                </p>
                <p><?php echo esc_html($listing['short_description'] ?? ''); ?></p>
                <a href="<?php echo add_query_arg('listing_id', $listing['listing_id'], get_permalink()); ?>"
                   class="btn btn-primary">View Details</a>
            </div>
        <?php endforeach; ?>

        <div class="portal-pagination">
            <?php if ($pagination['has_prev']): ?>
                <a href="<?php echo add_query_arg('page', $pagination['page'] - 1); ?>">Previous</a>
            <?php endif; ?>

            Page <?php echo $pagination['page']; ?> of <?php echo $pagination['total_pages']; ?>

            <?php if ($pagination['has_next']): ?>
                <a href="<?php echo add_query_arg('page', $pagination['page'] + 1); ?>">Next</a>
            <?php endif; ?>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('portal_listings', 'portal_listings_shortcode');
?>
```

### 3.2 Create Listing Detail Page

```php
<?php
/**
 * Display single listing detail
 */
function portal_listing_detail_shortcode($atts) {
    $listing_id = isset($_GET['listing_id']) ? intval($_GET['listing_id']) : 0;

    if (!$listing_id) {
        return '<p>Invalid listing.</p>';
    }

    $response = portal_api_request("/api/v1/listings/$listing_id");

    if (!$response) {
        return '<p>Listing not found.</p>';
    }

    ob_start();
    ?>
    <div class="portal-listing-detail">
        <h1><?php echo esc_html($response['title']); ?></h1>

        <div class="listing-info">
            <p><strong>Industry:</strong> <?php echo esc_html($response['industry'] ?? 'N/A'); ?></p>
            <p><strong>Region:</strong> <?php echo esc_html($response['region'] ?? 'N/A'); ?></p>
            <p><strong>Revenue Range:</strong> <?php echo esc_html($response['revenue_range'] ?? 'N/A'); ?></p>
            <p><strong>EBITDA Range:</strong> <?php echo esc_html($response['ebitda_range'] ?? 'N/A'); ?></p>
            <p><strong>Asking Price:</strong> <?php echo esc_html($response['asking_price_range'] ?? 'N/A'); ?></p>
        </div>

        <div class="listing-description">
            <h2>Description</h2>
            <p><?php echo esc_html($response['description'] ?? ''); ?></p>
        </div>

        <?php if (!empty($response['key_highlights'])): ?>
            <div class="listing-highlights">
                <h2>Key Highlights</h2>
                <ul>
                    <?php foreach ($response['key_highlights'] as $highlight): ?>
                        <li><?php echo esc_html($highlight); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <div class="listing-actions">
            <button id="express-interest-btn" data-listing-id="<?php echo $listing_id; ?>"
                    class="btn btn-primary btn-lg">I'm Interested</button>
        </div>
    </div>

    <script>
    jQuery(document).ready(function($) {
        $('#express-interest-btn').on('click', function() {
            var listingId = $(this).data('listing-id');
            var note = prompt('Add a note (optional):');

            // AJAX call to WordPress endpoint that will call Portal API
            $.post('<?php echo admin_url('admin-ajax.php'); ?>', {
                action: 'express_interest',
                listing_id: listingId,
                note: note
            }, function(response) {
                if (response.success) {
                    alert('Interest recorded! Our team will be in touch.');
                } else {
                    alert('Error: ' + response.data);
                }
            });
        });
    });
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('portal_listing_detail', 'portal_listing_detail_shortcode');
?>
```

### 3.3 Handle Interest Expression via AJAX

```php
<?php
/**
 * AJAX handler for expressing interest
 */
add_action('wp_ajax_express_interest', function() {
    if (!is_user_logged_in()) {
        wp_send_json_error('Please log in first.');
        return;
    }

    $listing_id = isset($_POST['listing_id']) ? intval($_POST['listing_id']) : 0;
    $note = isset($_POST['note']) ? sanitize_textarea_field($_POST['note']) : '';

    if (!$listing_id) {
        wp_send_json_error('Invalid listing ID.');
        return;
    }

    $user_id = get_current_user_id();
    $member_id = get_portal_member_id($user_id);

    if (!$member_id) {
        wp_send_json_error('Unable to resolve member ID.');
        return;
    }

    $data = [
        'member_id' => $member_id,
        'note' => $note,
    ];

    $response = portal_api_request("/api/v1/listings/$listing_id/interest", 'POST', $data);

    if ($response) {
        wp_send_json_success('Interest recorded successfully.');
    } else {
        wp_send_json_error('Failed to record interest. Please try again.');
    }
});
?>
```

## Step 4: Display Member Interests

```php
<?php
/**
 * Shortcode to display member's interests
 * Usage: [portal_my_interests]
 */
function portal_my_interests_shortcode() {
    if (!is_user_logged_in()) {
        return '<p>Please log in to view your interests.</p>';
    }

    $user_id = get_current_user_id();
    $member_id = get_portal_member_id($user_id);

    if (!$member_id) {
        return '<p>Unable to load interests.</p>';
    }

    $response = portal_api_request("/api/v1/members/$member_id/interests");

    if (!$response) {
        return '<p>Unable to load interests.</p>';
    }

    if (empty($response)) {
        return '<p>You haven\'t expressed interest in any listings yet.</p>';
    }

    ob_start();
    ?>
    <div class="portal-my-interests">
        <h2>My Interests</h2>
        <?php foreach ($response as $interest): ?>
            <div class="interest-card">
                <h3><?php echo esc_html($interest['listing']['title']); ?></h3>
                <p class="interest-meta">
                    <strong>Industry:</strong> <?php echo esc_html($interest['listing']['industry'] ?? 'N/A'); ?> |
                    <strong>Status:</strong> <?php echo esc_html($interest['status']); ?>
                </p>
                <?php if ($interest['note']): ?>
                    <p><strong>Your note:</strong> <?php echo esc_html($interest['note']); ?></p>
                <?php endif; ?>
                <p><small>Expressed on: <?php echo date('F j, Y', strtotime($interest['created_at'])); ?></small></p>
                <a href="<?php echo add_query_arg('listing_id', $interest['listing']['listing_id'], get_permalink()); ?>">
                    View Listing
                </a>
            </div>
        <?php endforeach; ?>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('portal_my_interests', 'portal_my_interests_shortcode');
?>
```

## Step 5: Display Engagement Dashboard

```php
<?php
/**
 * Shortcode to display engagement summary
 * Usage: [portal_engagement]
 */
function portal_engagement_shortcode() {
    if (!is_user_logged_in()) {
        return '<p>Please log in to view your engagement.</p>';
    }

    $user_id = get_current_user_id();
    $member_id = get_portal_member_id($user_id);

    if (!$member_id) {
        return '<p>Unable to load engagement data.</p>';
    }

    $response = portal_api_request("/api/v1/members/$member_id/engagement");

    if (!$response) {
        return '<p>Unable to load engagement data.</p>';
    }

    ob_start();
    ?>
    <div class="portal-engagement">
        <h2>My Engagement</h2>
        <div class="engagement-score">
            <h3>Engagement Score: <?php echo $response['engagement_score']; ?>/100</h3>
            <div class="score-bar" style="width: <?php echo $response['engagement_score']; ?>%;"></div>
        </div>

        <div class="engagement-stats">
            <div class="stat">
                <strong><?php echo $response['email_opens']; ?></strong>
                <span>Email Opens</span>
            </div>
            <div class="stat">
                <strong><?php echo $response['link_clicks']; ?></strong>
                <span>Link Clicks</span>
            </div>
            <div class="stat">
                <strong><?php echo $response['form_submissions']; ?></strong>
                <span>Form Submissions</span>
            </div>
        </div>

        <?php if (!empty($response['recent_events'])): ?>
            <div class="recent-activity">
                <h3>Recent Activity</h3>
                <ul>
                    <?php foreach ($response['recent_events'] as $event): ?>
                        <li>
                            <strong><?php echo esc_html($event['event_type']); ?></strong>
                            - <?php echo esc_html($event['subject'] ?? 'N/A'); ?>
                            <br><small><?php echo date('F j, Y g:i a', strtotime($event['occurred_at'])); ?></small>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('portal_engagement', 'portal_engagement_shortcode');
?>
```

## Security Best Practices

1. **Never expose API key to browser/JavaScript**
2. **Always make API calls from server-side PHP**
3. **Use HTTPS for all communication**
4. **Validate and sanitize all user inputs**
5. **Implement nonce verification for AJAX requests**
6. **Log API errors for debugging (but not sensitive data)**

## Error Handling

```php
<?php
// Add error logging
function portal_log_error($message, $context = []) {
    if (defined('WP_DEBUG') && WP_DEBUG) {
        error_log('Portal API: ' . $message . ' | Context: ' . json_encode($context));
    }
}

// Enhanced error handling
function portal_api_request_with_retry($endpoint, $method = 'GET', $data = null, $retries = 3) {
    for ($i = 0; $i < $retries; $i++) {
        $response = portal_api_request($endpoint, $method, $data);

        if ($response !== null) {
            return $response;
        }

        portal_log_error("API request failed, retry $i/$retries", [
            'endpoint' => $endpoint,
            'method' => $method
        ]);

        sleep(1); // Wait 1 second before retry
    }

    return null;
}
?>
```

## Testing

1. **Test member resolution:**
   - Register new user via Ultimate Member
   - Check Portal API logs for member creation
   - Verify `_portal_member_id` user meta

2. **Test listings display:**
   - Add `[portal_listings]` shortcode to a page
   - Verify listings load correctly
   - Test pagination

3. **Test interest expression:**
   - Click "I'm Interested" button
   - Verify interest is recorded in Portal API
   - Check CRM for activity creation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key missing" error | Verify PORTAL_API_KEY is defined and correct |
| "Member not found" error | Check member resolution ran successfully on login/approval |
| Listings not loading | Check API base URL, verify network connectivity |
| Interest not recording | Verify member_id is valid, check API logs |

---

For more details, see:
- [API Usage Guide](api_usage.md)
- [Architecture Documentation](architecture.md)
