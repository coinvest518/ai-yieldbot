# Telegram Bot Reference Information

## Bot Details
**Bot Name:** YBot AI  
**Bot Username:** @ybotai_bot  
**Bot Link:** https://t.me/ybotai_bot  
**Bot Token:** <REDACTED - DO NOT STORE SECRETS IN THE REPOSITORY>  

> WARNING: A Telegram Bot Token was previously committed to this file. That secret has been removed from this file in the current commit. If this token is still active, revoke it immediately and create a new token. Store bot tokens in a local `.env` file and never commit them to git. See the repository README or follow the steps below to purge the secret from history and rotate credentials.

## Composio Integration
**Connected Account ID:** ca_ZPVfCDk6sSxt  
**Toolkit:** TELEGRAM  

## Bot Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot and get a welcome message |
| `/verify` | Verify as a real user (first step) |
| `/auth` | Link your crypto wallet (for later) |
| `/help` | Get help and see all commands |
| `/rules` | Show group rules |
| `/dao` | View active DAO proposals and votes |
| `/stats` | Show community/DAO stats (active users, tokens staked) |
| `/feedback` | Send feedback to the team |
| `/support` | Contact support |
| `/settings` | Change your bot settings |
| `/profile` | View your profile (verification status, wallet, etc.) |
| `/invite` | Get the group invite link |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/mute` | Mute a user (admin only) |
| `/unmute` | Unmute a user (admin only) |
| `/ban` | Ban a user (admin only) |
| `/kick` | Kick a user (admin only) |
| `/announce` | Post an announcement (admin only) |
| `/poll` | Create a poll (admin only) |

## Bot Capabilities
The Telegram bot serves as the community interface for Yieldbot:

1. **User Verification** - Verify users before joining community
2. **Wallet Linking** - Connect crypto wallets for DeFi features
3. **DAO Governance** - View and participate in proposals
4. **Community Stats** - Track engagement and staking metrics
5. **Moderation** - Admin tools for community management
6. **Announcements** - Broadcast updates to community
7. **Support** - User feedback and support channels

## Integration with Main Agent
The main AI agent can control the Telegram bot to:
- Send announcements about $YBOT updates
- Post DAO proposal notifications
- Share yield farming stats
- Respond to support requests
- Moderate community discussions

## Monitoring Subagent
A dedicated monitoring subagent (`src/telegram_monitor.py`) can:
- Poll for new messages using `TELEGRAM_GET_UPDATES`
- Auto-respond to commands (/start, /help, /rules, etc.)
- Answer Yieldbot questions
- Flag important messages for main agent

### Running the Monitor:
```bash
# Single check (test mode)
python -m src.telegram_monitor --once

# Continuous monitoring (every 30 mins)
python -m src.telegram_monitor

# Custom interval (in seconds, e.g., 1 hour = 3600)
python -m src.telegram_monitor 3600
```

## Composio Telegram Tools Available
| Tool | Description |
|------|-------------|
| `TELEGRAM_GET_UPDATES` | Poll for new messages/events |
| `TELEGRAM_GET_CHAT_HISTORY` | Get past messages |
| `TELEGRAM_SEND_MESSAGE` | Send text messages |
| `TELEGRAM_SEND_PHOTO` | Send images |
| `TELEGRAM_SEND_POLL` | Create polls |
| `TELEGRAM_DELETE_MESSAGE` | Delete messages |
| `TELEGRAM_GET_CHAT` | Get chat info |
| `TELEGRAM_GET_CHAT_ADMINISTRATORS` | List admins |
| And more... | 17 tools total |

## API Reference
Telegram Bot API: https://core.telegram.org/bots/api
