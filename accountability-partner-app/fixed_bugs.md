# Fixed Bugs: GrowthPact

This document tracks resolved bugs with root causes and solutions to prevent regression and share knowledge.

---

## Template

```markdown
### Bug #XXX: [Short Description]
**Date Fixed**: YYYY-MM-DD
**Severity**: Critical | High | Medium | Low
**Affected Component**: Backend | Frontend | Database | Infrastructure

**Symptoms**:
- What the user/developer experienced

**Root Cause**:
- Technical explanation of what caused the bug

**Solution**:
- How it was fixed
- Code changes made

**Prevention**:
- Tests added
- Safeguards implemented
- Documentation updated

**Related Issues**: #123, #456
```

---

## Resolved Bugs

_No bugs reported yet - project is in initial development phase._

---

## Common Pitfalls (Preventive Documentation)

### Backend

#### Async/Await Consistency
**Issue**: Mixing sync and async code causes errors
**Prevention**:
- Always use `async def` for database operations
- Always `await` async function calls
- Use `AsyncSession` consistently with SQLAlchemy

```python
# ❌ Wrong
def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

# ✅ Correct
async def get_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()
```

#### N+1 Query Problem
**Issue**: Loading relationships in loops causes excessive queries
**Prevention**:
- Use `selectinload()` or `joinedload()` for eager loading
- Monitor query count in tests

```python
# ❌ Wrong (N+1 queries)
partnerships = await db.execute(select(Partnership).filter(...))
for p in partnerships.scalars():
    print(p.user1.email)  # Triggers query per partnership

# ✅ Correct
partnerships = await db.execute(
    select(Partnership)
    .options(selectinload(Partnership.user1))
    .filter(...)
)
```

#### Password Hashing
**Issue**: Comparing plaintext passwords with hashes
**Prevention**:
- Never store passwords in plaintext
- Always use `verify_password()` for comparison

```python
# ❌ Wrong
if user.password_hash == password:
    ...

# ✅ Correct
from app.core.security import verify_password
if verify_password(password, user.password_hash):
    ...
```

### Frontend

#### State Updates with Stale Data
**Issue**: React state updates don't reflect latest data
**Prevention**:
- Use functional setState with callbacks
- Use React Query for server state

```typescript
// ❌ Wrong
setCount(count + 1)

// ✅ Correct
setCount((prev) => prev + 1)
```

#### Missing Error Boundaries
**Issue**: Component errors crash entire app
**Prevention**:
- Wrap features in error boundaries
- Show fallback UI on error

```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <FeatureComponent />
</ErrorBoundary>
```

### Database

#### Missing Indexes
**Issue**: Slow queries on frequently accessed columns
**Prevention**:
- Index foreign keys
- Index columns used in WHERE clauses
- Monitor query performance

```sql
-- Add indexes during migration
CREATE INDEX idx_partnerships_user1 ON partnerships(user1_id);
CREATE INDEX idx_check_ins_partnership ON check_ins(partnership_id);
```

#### Race Conditions
**Issue**: Concurrent updates cause data inconsistency
**Prevention**:
- Use database transactions
- Implement optimistic locking where needed

```python
async with db.begin():  # Transaction
    # Multiple operations
    await db.commit()
```

---

## Debug Checklist

When encountering a bug:

1. **Reproduce**: Can you consistently reproduce it?
2. **Isolate**: Minimum code to trigger the bug?
3. **Log**: What do the logs say?
4. **Test**: Write a failing test first
5. **Fix**: Implement the fix
6. **Verify**: Confirm test now passes
7. **Document**: Add to this file

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Bugs Fixed**: 0
**Maintained By**: Autonomous Development Agent
