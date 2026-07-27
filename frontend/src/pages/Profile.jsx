import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useApi } from "../hooks/useApi";
import { useFetch } from "../hooks/useFetch";

export default function Profile() {
  const { user, setUser } = useAuth();
  const api = useApi();
  const { data, error, loading, refetch } = useFetch("/api/auth/me");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) {
      setUploadError("Choose an image first.");
      return;
    }
    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await api.upload("/auth/me/avatar", formData);
      setUploadSuccess("Avatar updated.");
      setUser((prev) =>
        prev
          ? {
              ...prev,
              profile: result.profile,
            }
          : prev
      );
      refetch();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  const profile = data?.profile || user?.profile;

  return (
    <main className="page">
      <h1>Profile</h1>
      <p className="lede">Update your avatar via Cloudinary-backed upload.</p>

      {loading && <p className="status">Loading profile…</p>}
      {error && <p className="error">{error.message}</p>}

      {data && (
        <section className="panel">
          <div className="avatar-row">
            {profile?.avatar_url ? (
              <img
                className="avatar"
                src={profile.avatar_url}
                alt={profile.display_name}
              />
            ) : (
              <div className="avatar placeholder">
                {(profile?.display_name || data.username || "?").slice(0, 1)}
              </div>
            )}
            <dl className="meta">
              <div>
                <dt>Username</dt>
                <dd>{data.username}</dd>
              </div>
              <div>
                <dt>Display name</dt>
                <dd>{profile?.display_name}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>{data.email}</dd>
              </div>
            </dl>
          </div>

          <form className="auth-form" onSubmit={handleUpload}>
            <label>
              Avatar image
              <input
                type="file"
                accept="image/png,image/jpeg,image/gif,image/webp"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
            {uploading && <p className="status">Uploading…</p>}
            {uploadError && <p className="error">{uploadError}</p>}
            {uploadSuccess && <p className="success">{uploadSuccess}</p>}
            <button type="submit" disabled={uploading}>
              Upload to Cloudinary
            </button>
          </form>
        </section>
      )}
    </main>
  );
}
