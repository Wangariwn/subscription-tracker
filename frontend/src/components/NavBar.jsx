import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function NavBar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();

  return (
    <header className="nav">
      <Link to="/" className="brand">
        Subscription Tracker
      </Link>
      <nav className="nav-links">
        {isAuthenticated ? (
          <>
            <NavLink to="/" end>
              Dashboard
            </NavLink>
            <NavLink to="/subscriptions">Subscriptions</NavLink>
            <NavLink to="/catalog">Catalog</NavLink>
            {isAdmin && (
              <>
                <NavLink to="/admin/analytics">Analytics</NavLink>
                <NavLink to="/admin/subscriptions">All subscriptions</NavLink>
                <NavLink to="/admin/users">Users</NavLink>
              </>
            )}
            <NavLink to="/profile">Profile</NavLink>
            <span className="nav-user">
              {user?.username}
              {isAdmin ? " · admin" : ""}
            </span>
            <button type="button" className="linkish" onClick={logout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
