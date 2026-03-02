#!/usr/bin/env python3
"""
Create a simple HTML page to test admin messaging from browser
"""

html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Admin Messaging Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        textarea { width: 100%; padding: 10px; }
        .success { color: green; }
        .error { color: red; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1>🧪 Admin Messaging Diagnostic Test</h1>
    
    <div class="section">
        <h2>1. Check Backend Connection</h2>
        <button onclick="testBackendHealth()">Test Backend Health</button>
        <div id="healthResult"></div>
    </div>
    
    <div class="section">
        <h2>2. Test Admin Login</h2>
        <button onclick="testAdminLogin()">Test Admin Login</button>
        <div id="loginResult"></div>
        <input type="hidden" id="adminToken" value="">
    </div>
    
    <div class="section">
        <h2>3. Fetch All Messages</h2>
        <button onclick="testFetchMessages()">Fetch Messages</button>
        <div id="messagesResult"></div>
    </div>
    
    <div class="section">
        <h2>4. Send Response to First Message</h2>
        <textarea id="responseText" placeholder="Enter response here..." rows="3"></textarea>
        <button onclick="testSendResponse()">Send Response</button>
        <div id="responseResult"></div>
    </div>

    <script>
        const API_URL = 'http://192.168.1.3:5000/api';
        
        function log(elementId, message, type = 'info') {
            const elem = document.getElementById(elementId);
            const color = type === 'success' ? 'green' : type === 'error' ? 'red' : 'blue';
            elem.innerHTML += `<p style="color: ${color};">${message}</p>`;
            console.log(message);
        }
        
        async function testBackendHealth() {
            log('healthResult', '⏳ Testing backend...');
            try {
                const response = await fetch('http://192.168.1.3:5000/api/health');
                const data = await response.json();
                log('healthResult', `✅ Backend is running: ${data.status}`, 'success');
            } catch (err) {
                log('healthResult', `❌ Backend connection failed: ${err.message}`, 'error');
            }
        }
        
        async function testAdminLogin() {
            log('loginResult', '⏳ Logging in as admin...');
            try {
                const response = await fetch(`${API_URL}/auth/login/json`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'admin@masjid.com',
                        password: 'admin123'
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const token = data.access_token;
                    document.getElementById('adminToken').value = token;
                    log('loginResult', `✅ Admin logged in. Token: ${token.substring(0, 30)}...`, 'success');
                } else {
                    log('loginResult', `❌ Login failed: ${response.status}`, 'error');
                }
            } catch (err) {
                log('loginResult', `❌ Login error: ${err.message}`, 'error');
            }
        }
        
        async function testFetchMessages() {
            const token = document.getElementById('adminToken').value;
            if (!token) {
                log('messagesResult', '❌ Please login first', 'error');
                return;
            }
            
            log('messagesResult', '⏳ Fetching messages...');
            try {
                const response = await fetch(`${API_URL}/messages/admin/all`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.ok) {
                    const messages = await response.json();
                    log('messagesResult', `✅ Fetched ${messages.length} messages`, 'success');
                    messages.forEach((msg, i) => {
                        log('messagesResult', `${i+1}. ID: ${msg.id} - From: ${msg.student_name}`);
                    });
                } else {
                    log('messagesResult', `❌ Fetch failed: ${response.status}`, 'error');
                }
            } catch (err) {
                log('messagesResult', `❌ Fetch error: ${err.message}`, 'error');
            }
        }
        
        async function testSendResponse() {
            const token = document.getElementById('adminToken').value;
            const responseText = document.getElementById('responseText').value;
            
            if (!token) {
                log('responseResult', '❌ Please login first', 'error');
                return;
            }
            if (!responseText.trim()) {
                log('responseResult', '❌ Please enter a response', 'error');
                return;
            }
            
            log('responseResult', '⏳ Sending response...');
            
            try {
                // Get first message ID
                const messagesResponse = await fetch(`${API_URL}/messages/admin/all`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const messages = await messagesResponse.json();
                
                if (messages.length === 0) {
                    log('responseResult', '❌ No messages to respond to', 'error');
                    return;
                }
                
                const messageId = messages[0].id;
                log('responseResult', `Responding to message ID: ${messageId}`);
                
                // Send response
                const response = await fetch(`${API_URL}/messages/admin/${messageId}/respond`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ response: responseText })
                });
                
                const responseData = await response.json();
                
                if (response.ok) {
                    log('responseResult', `✅ Response sent successfully!`, 'success');
                    log('responseResult', `Response: ${JSON.stringify(responseData, null, 2)}`);
                } else {
                    log('responseResult', `❌ Failed: ${response.status}`, 'error');
                    log('responseResult', `Error: ${JSON.stringify(responseData, null, 2)}`, 'error');
                }
            } catch (err) {
                log('responseResult', `❌ Error: ${err.message}`, 'error');
            }
        }
        
        // Auto-test on load
        window.onload = function() {
            testBackendHealth();
        };
    </script>
</body>
</html>
'''

with open(r'c:\Users\lenovo\Desktop\noori\backend\test_messaging.html', 'w') as f:
    f.write(html_content)

print("✅ Test page created at: c:\\Users\\lenovo\\Desktop\\noori\\backend\\test_messaging.html")
print("\nOpen this file in your browser to manually test the messaging system.")
print("Steps:")
print("1. Open the HTML file")
print("2. Click 'Test Backend Health'")
print("3. Click 'Test Admin Login'")
print("4. Click 'Fetch Messages'")
print("5. Type a response and click 'Send Response'")
