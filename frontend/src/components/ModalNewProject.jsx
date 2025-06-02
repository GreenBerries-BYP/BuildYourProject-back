import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewProject.css";
import api from "../api/api";
import { useTranslation } from "react-i18next";

import { getToken } from "../auth/auth";
import { abntTemplates } from "../mocks/abntMock";

const ModalNewProject = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const modalRef = useRef();
  const descriptionTextareaRef = useRef(null);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    type: "TCC",
    phases: [],
    collaborators: [],
    startDate: "",
    endDate: "",
  });

  const [emailInput, setEmailInput] = useState("");
  const [emailError, setEmailError] = useState("");
  const [formErrors, setFormErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) {
      setFormErrors((prev) => ({ ...prev, [name]: "" }));
    }
    if (name === "description") {
      setTimeout(() => autoResizeTextarea(descriptionTextareaRef.current), 0);
    }
  };

  const handleTypeChange = (type) => {
    setFormData((prev) => ({ ...prev, type: type }));
    if (formErrors.type) {
      setFormErrors((prev) => ({ ...prev, type: "" }));
    }
  };

  const handlephasesChange = (selectedphasesValue) => {
    setFormData((prevData) => {
      const currentphasess = prevData.phases;
      if (currentphasess.includes(selectedphasesValue)) {
        return {
          ...prevData,
          phases: currentphasess.filter((tmpl) => tmpl !== selectedphasesValue),
        };
      } else {
        return {
          ...prevData,
          phases: [...currentphasess, selectedphasesValue],
        };
      }
    });
  };

  const handleCollaboratorChange = (newColaboradores) => {
    setFormData((prev) => ({ ...prev, collaborators: newColaboradores }));
  };

  const adicionarColaborador = () => {
    if (!emailInput.trim()) {
      setEmailError(t("messages.emailCantBeEmpty"));
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)) {
      setEmailError(t("messages.invalidEmailFormat"));
      return;
    }

    if (formData.collaborators.includes(emailInput)) {
      setEmailError(t("messages.emailAlreadyAdded"));
      return;
    }

    handleCollaboratorChange([...formData.collaborators, emailInput]);
    setEmailInput("");
    setEmailError("");
  };

  const removerColaborador = (email) => {
    handleCollaboratorChange(formData.collaborators.filter((e) => e !== email));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      adicionarColaborador();
    }
  };

  const prevStep = () => setCurrentStep((prev) => prev - 1);

  const validateForm = () => {
    const errors = {};
    if (!formData.name.trim()) errors.name = t("messages.projectNameRequired");
    if (!formData.description.trim())
      errors.description = t("messages.projectDescriptionRequired");

    if (!formData.startDate) {
      errors.startDate = t("messages.startDateRequired");
    }
    if (!formData.endDate) {
      errors.endDate = t("messages.endDateRequired");
    } else if (formData.startDate && formData.endDate) {
      const start = new Date(formData.startDate);
      const end = new Date(formData.endDate);
      if (end < start) {
        errors.endDate = t("messages.endDateAfterStartDate");
      }
    }
    return errors;
  };

  const nextStep = () => {
    let currentStepErrors = {};
    const allErrors = validateForm();

    if (currentStep === 1) {
      if (allErrors.name) currentStepErrors.name = allErrors.name;
      if (allErrors.description)
        currentStepErrors.description = allErrors.description;
    } else if (currentStep === 2) {
      if (allErrors.startDate)
        currentStepErrors.startDate = allErrors.startDate;
      if (allErrors.endDate) currentStepErrors.endDate = allErrors.endDate;
    }

    if (Object.keys(currentStepErrors).length > 0) {
      setFormErrors((prevErrors) => ({ ...prevErrors, ...currentStepErrors }));
      return;
    }

    let relevantErrorKeys = [];
    if (currentStep === 1) relevantErrorKeys = ["name", "description"];
    if (currentStep === 2) relevantErrorKeys = ["startDate", "endDate"];

    const newErrors = { ...formErrors };

    relevantErrorKeys.forEach((key) => {
      if (newErrors[key] && !currentStepErrors[key]) {
        delete newErrors[key];
      }
    });
    if (Object.keys(currentStepErrors).length === 0) {
      relevantErrorKeys.forEach((key) => delete newErrors[key]);
    }

    setFormErrors(newErrors);
    setCurrentStep((prev) => prev + 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (currentStep === 3) {
      const allErrors = validateForm();
      if (Object.keys(allErrors).length > 0) {
        setFormErrors(allErrors);
        if (allErrors.name || allErrors.description) {
          setCurrentStep(1);
        } else if (allErrors.startDate || allErrors.endDate) {
          setCurrentStep(2);
        }
        return;
      }
      setFormErrors({});
      setLoading(true);
      try {
        const token = getToken();
        const submissionData = {
          name: formData.name,
          description: formData.description,
          type: formData.type,
          collaborators: formData.collaborators,
          phases: formData.phases,
          startDate: formData.startDate,
          endDate: formData.endDate,
        };
        // Add a comment about backend dependency
        // TODO: Ensure backend endpoint /api/projetos/ is fully implemented and handles auth correctly.
        const response = await api.post("/projetos/", submissionData, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          handleErrorLocally: true, // Add this flag
        });

        if (
          response.status &&
          response.status >= 200 &&
          response.status < 300
        ) {
          // Successful creation
          onClose();
          setFormData({
            name: "",
            description: "",
            type: "TCC",
            phases: [],
            collaborators: [],
            startDate: "",
            endDate: "",
          });
          setCurrentStep(1);
          setEmailInput("");
          setFormErrors({});
          setIsDescriptionExpanded(false);

          location.reload();
        } else {
          // This block might not be strictly necessary if Axios throws on non-2xx by default
          // For safety, keeping a generic error if it somehow reaches here
          const errorData = response.data;
          throw new Error(errorData.detail || t("messages.errorNewProject"));
        }
      } catch (err) {
        if (err.response?.status === 401) {
          setFormErrors({
            submit: t("messages.errorNewProjectBackendNotReady"),
          });
        } else if (err.response) {
          // Other HTTP errors (400, 500, etc.)
          const errorData = err.response.data;
          let detailedMessage = "";
          if (typeof errorData === "object" && errorData !== null) {
            // Try to extract messages if backend sends structured errors like DRF
            detailedMessage = Object.values(errorData).flat().join(" ");
          }
          setFormErrors({
            submit: `${t("messages.errorNewProject")} ${
              detailedMessage || err.message
            }`.trim(),
          });
        } else {
          // Network errors or other issues
          setFormErrors({
            submit: err.message || t("messages.errorNewProject"),
          });
        }
      } finally {
        setLoading(false);
      }
    } else {
      nextStep();
    }
  };

  const autoResizeTextarea = (element) => {
    if (element) {
      element.style.height = "auto";
      const computedStyle = getComputedStyle(element);
      const maxHeight = parseInt(computedStyle.maxHeight, 10);

      if (!isNaN(maxHeight) && element.scrollHeight > maxHeight) {
        element.style.height = `${maxHeight}px`;
        element.style.overflowY = "auto";
      } else {
        element.style.height = `${element.scrollHeight}px`;
        element.style.overflowY = "hidden";
      }
    }
  };

  useEffect(() => {
    if (currentStep === 1 && descriptionTextareaRef.current) {
      autoResizeTextarea(descriptionTextareaRef.current);
    }
  }, [formData.description, currentStep]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  if (!isOpen) return null;

  const projectTypes = ["TCC", t("inputs.academicArticle"), "ABNT"];

  return (
    <div className="modal-overlay">
      <div className="modal-content" ref={modalRef}>
        <div className="modal-header">
          <h2>{t("titles.newProject")}</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="step-indicator">
            <div
              className={`step-item ${currentStep === 1 ? "active" : ""} ${
                currentStep > 1 ? "completed" : ""
              }`}
            >
              <span className="step-number">1</span>
              <span className="step-label">{t("steps.basicInfo")}</span>
            </div>
            <div className="step-connector"></div>
            <div
              className={`step-item ${currentStep === 2 ? "active" : ""} ${
                currentStep > 2 ? "completed" : ""
              }`}
            >
              <span className="step-number">2</span>
              <span className="step-label">
                {t("steps.datesAndCollaborators")}
              </span>
            </div>
            <div className="step-connector"></div>
            <div className={`step-item ${currentStep === 3 ? "active" : ""}`}>
              <span className="step-number">3</span>
              <span className="step-label">{t("steps.review")}</span>
            </div>
          </div>
          <form onSubmit={handleSubmit} noValidate>
            {currentStep === 1 && (
              <div>
                <h3>{t("titles.step1BasicInfo")}</h3>
                <div className="form-grid">
                  <div className="form-left">
                    <div className="input-group">
                      <label htmlFor="projectName">{t("inputs.name")}</label>
                      <input
                        id="projectName"
                        name="name"
                        placeholder={t("placeholders.projectName")}
                        value={formData.name}
                        onChange={handleChange}
                      />
                      {formErrors.name && (
                        <p className="input-error">{formErrors.name}</p>
                      )}
                    </div>
                    <div
                      className={`input-group floating-label-group ${
                        formData.description ? "has-value" : ""
                      } ${formErrors.description ? "has-error" : ""}`}
                      onClick={() =>
                        descriptionTextareaRef.current &&
                        descriptionTextareaRef.current.focus()
                      }
                    >
                      <textarea
                        id="projectDescription"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        onFocus={(e) =>
                          e.target.parentElement.classList.add("focused")
                        }
                        onBlur={(e) => {
                          if (!formData.description) {
                            e.target.parentElement.classList.remove("focused");
                          }
                        }}
                        ref={descriptionTextareaRef}
                        rows="4"
                      />
                      <label htmlFor="projectDescription">
                        {t("inputs.description")}
                      </label>
                      <div className="char-counter-footer">
                        <span>{formData.description.length} / 500</span>
                      </div>
                    </div>
                    {formErrors.description && (
                      <p
                        className="input-error"
                        style={{ marginTop: "-0.5rem" }}
                      >
                        {formErrors.description}
                      </p>
                    )}
                  </div>
                  <div className="form-right">
                    <div className="form-options">
                      <div className="project-type">
                        <label>{t("inputs.projectType")}</label>
                        <div className="options">
                          {projectTypes.map((type) => (
                            <button
                              key={type}
                              type="button"
                              onClick={() => handleTypeChange(type)}
                              className={
                                formData.type === type ? "selected" : ""
                              }
                            >
                              {type}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="phases mt-4">
                        <label htmlFor="projectphases">
                          {t("inputs.phases")}
                        </label>
                        <div className="options">
                          {abntTemplates.map((tmpl) => (
                            <button
                              key={tmpl.value}
                              type="button"
                              onClick={() => handlephasesChange(tmpl?.value)}
                              className={
                                formData.phases.includes(tmpl?.value)
                                  ? "selected"
                                  : ""
                              }
                            >
                              {t(tmpl?.label)}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {currentStep === 2 && (
              <div>
                <h3>{t("titles.step2DatesAndCollabs")}</h3>
                <div className="form-grid">
                  <div className="form-left">
                    <div className="input-group">
                      <label htmlFor="startDate">{t("inputs.startDate")}</label>
                      <input
                        type="date"
                        id="startDate"
                        name="startDate"
                        value={formData.startDate}
                        onChange={handleChange}
                      />
                      {formErrors.startDate && (
                        <p className="input-error">{formErrors.startDate}</p>
                      )}
                    </div>
                    <div className="input-group">
                      <label htmlFor="endDate">{t("inputs.endDate")}</label>
                      <input
                        type="date"
                        id="endDate"
                        name="endDate"
                        value={formData.endDate}
                        onChange={handleChange}
                      />
                      {formErrors.endDate && (
                        <p className="input-error">{formErrors.endDate}</p>
                      )}
                    </div>
                  </div>
                  <div className="form-right">
                    <h4>{t("titles.collaborators")}</h4>
                    <div className="input-group">
                      <input
                        id="collaboratorEmail"
                        type="email"
                        placeholder={t("messages.emailMessage")}
                        value={emailInput}
                        onChange={(e) => {
                          setEmailInput(e.target.value);
                          setEmailError("");
                        }}
                        onKeyDown={handleKeyDown}
                      />
                    </div>
                    {emailError && (
                      <p
                        className="input-error"
                        style={{ marginTop: "0.5rem" }}
                      >
                        {emailError}
                      </p>
                    )}
                    <div className="email-list">
                      {formData.collaborators.map((email) => (
                        <span key={email} className="email-chip">
                          {email}
                          <button
                            type="button"
                            onClick={() => removerColaborador(email)}
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
            {currentStep === 3 && (
              <div>
                <h3>{t("titles.step3Review")}</h3>
                <p className="review-intro-message">
                  {t("messages.reviewProjectDetails")}
                </p>
                <div className="review-grid">
                  <div className="review-section">
                    <h4>{t("titles.projectDetails")}</h4>
                    <p>
                      <strong>{t("inputs.name")}:</strong>{" "}
                      {formData.name || t("messages.notSpecified")}
                    </p>

                    <div className="review-item review-description-wrapper">
                      <p style={{ marginBottom: "0.5rem" }}>
                        <strong>{t("inputs.descriptionShort")}:</strong>
                      </p>
                      <div
                        className={`review-description-content ${
                          isDescriptionExpanded ? "expanded" : "collapsed"
                        }`}
                      >
                        {formData.description || t("messages.notSpecified")}
                      </div>
                      {formData.description &&
                        formData.description.length > 150 && (
                          <button
                            type="button"
                            onClick={() =>
                              setIsDescriptionExpanded(!isDescriptionExpanded)
                            }
                            className="toggle-description-btn"
                          >
                            {isDescriptionExpanded
                              ? t("buttons.readLess")
                              : t("buttons.readMore")}
                          </button>
                        )}
                    </div>

                    <p>
                      <strong>{t("inputs.projectType")}:</strong>{" "}
                      {t(formData.type) || t("messages.notSpecified")}
                    </p>
                    <p>
                      <strong>{t("inputs.phases")}:</strong>{" "}
                      {formData.phases.length > 0
                        ? formData.phases
                            .map((value) =>
                              t(
                                (
                                  abntTemplates.find(
                                    (tmpl) => tmpl?.value === value
                                  ) || {}
                                ).label
                              )
                            )
                            .join(", ")
                        : t("messages.notSpecified")}
                    </p>
                  </div>
                  <div className="review-section">
                    <h4>{t("titles.datesAndCollaborators")}</h4>
                    <p>
                      <strong>{t("inputs.startDate")}:</strong>{" "}
                      {formData.startDate || t("messages.notSpecified")}
                    </p>
                    <p>
                      <strong>{t("inputs.endDate")}:</strong>{" "}
                      {formData.endDate || t("messages.notSpecified")}
                    </p>
                    <p>
                      <strong>{t("titles.collaborators")}:</strong>
                    </p>
                    {formData.collaborators.length > 0 ? (
                      <ul className="review-collaborators-list">
                        {formData.collaborators.map((email) => (
                          <li key={email}>{email}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>{t("messages.noCollaborators")}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="navigation-buttons">
              {currentStep > 1 && (
                <button type="button" className="prev-btn" onClick={prevStep}>
                  {t("buttons.previous")}
                </button>
              )}
              {currentStep < 3 && (
                <button type="button" className="next-btn" onClick={nextStep}>
                  {t("buttons.next")}
                </button>
              )}
              {currentStep === 3 && (
                <button type="submit" className="save-btn" disabled={loading}>
                  {loading ? t("buttons.saving") : t("buttons.createProject")}
                </button>
              )}
            </div>
            {formErrors.submit && (
              <p className="input-error center" style={{ marginTop: "10px" }}>
                {formErrors.submit}
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};
export default ModalNewProject;
