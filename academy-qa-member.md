Template: 
1. Decisions and notes while drafting the learning path will be marked as quote blocks with a > at the beginning of the line.
2. The Stages in the user journey should be marked with a ## (double hash) at the beginning of the line. They will be heading two.
3. Each asset will be in heading 4 with four hashes at the beginning of the line.

<details>
  <summary>Template for writing the script for each video:</summary>

Objective statement: It should be a single or two line statement that describes the goal of the video.

1. (Screen where the video will be recorded): Describe the action to be taken on that screen in as much detail as possible. It may contain <attachments> in a placeholder like format to signify if something may be unclear for the person who is reading and recording the video.

This will be the narration on the video. It will be spoken by the narrator, word for word, to the letter. It needs to be clear, concise, and easy to follow.

</details>

<details>
  <summary>Outline for learning path of Member role</summary>
 
- User is invited to the workspace and they sign up.
- User after signing up, lands on the Project Page.
- User is introduced to Roles and role permissions.
- General Workflow is outlined (Cases → Results → Defects)
- Importing test cases from other tools
- Repository Management
  - Shared steps
  - System fields: Modify
  - Custom fields: create, edit, and delete
  - Parameters
  - Tags
  - Integrations: Linking external issues with test cases.
- Test plans and Test runs
    - Test runs wizard
    - Bulk Actions
    - Assignment
    - Test run settings
    - Linking external issues with test runs
- Defects management
    - Filing a defect for a result, from a test run.
    - Defects list
    - Linking external issues with defects.
    - Filing external issues directly from a test run.
- Dashboard: track your efforts
- Other Integrations & API
</details>

- [User is invited to the workspace and they sign up.](#user-is-invited-to-the-workspace-and-they-sign-up)
  - [(103) What is a workspace?](#103-what-is-a-workspace)
  - [(104) Joining your workspace](#104-joining-your-workspace)
  - [(104) Accidental signup?](#104-accidental-signup)
  - [(30) Issue - this invite is for another user](#30-issue---this-invite-is-for-another-user)
  - [(xx) Sign up process when teams use SSO and SCIM](#xx-sign-up-process-when-teams-use-sso-and-scim)
- [User after signing up, lands on the Project Page.](#user-after-signing-up-lands-on-the-project-page)
  - [(68) Finding your way around the workspace](#68-finding-your-way-around-the-workspace)
  - [(102) Personalize: Picture and theme](#102-personalize-picture-and-theme)
  - [(xx) Help is just a click away!](#xx-help-is-just-a-click-away)
- [Introduction to Roles](#introduction-to-roles)
  - [(106) Who's Who in Your Workspace?](#106-whos-who-in-your-workspace)
  - [(107) What's my role?](#107-whats-my-role)
- [General Workflow (Cases → Results → Defects)](#general-workflow-cases--results--defects)
  - [(83) What's a project?](#83-whats-a-project)
  - [(109) Organizing with test suites](#109-organizing-with-test-suites)
  - [(110) Creating (quick) test cases](#110-creating-quick-test-cases)
  - [(111) Anatomy of a test case](#111-anatomy-of-a-test-case)
  - [(112) Executing your tests](#112-executing-your-tests)
  - [(113) Filing your first defect](#113-filing-your-first-defect)
- [Repository Management](#repository-management)
  - [(114) Repository management: TASKTIDES](#114-repository-management-tasktides)
  - [(115) Repository: tree vs folder view](#115-repository-tree-vs-folder-view)
  - [(116) Bulk deletion in the repository](#116-bulk-deletion-in-the-repository)
  - [(117) Search and Filters](#117-search-and-filters)
  - [(89) Trash bin](#89-trash-bin)
  - [Shared Steps](#shared-steps)
    - [(86) Save time with Shared steps](#86-save-time-with-shared-steps)
  - [System fields: Modify](#system-fields-modify)
    - [(21) Modifying system fields](#21-modifying-system-fields)
    - [(19) Understanding the automation status field](#19-understanding-the-automation-status-field)
  - [Custom fields: create, edit, and delete](#custom-fields-create-edit-and-delete)
    - [(28) Custom fields - distribution widget](#28-custom-fields---distribution-widget)
    - [(27) System fields - results status](#27-system-fields---results-status)
    - [(26) Custom fields - QQL](#26-custom-fields---qql)
    - [(25) Custom fields - API](#25-custom-fields---api)
    - [(23) Custom fields - order](#23-custom-fields---order)
    - [(22) Custom fields - create](#22-custom-fields---create)
  - [Parameters](#parameters)
  - [Tags](#tags)
    - [(99) Workspace - tags](#99-workspace---tags)
  - [Integrations: Repository](#integrations-repository)
    - [(122) Linking external issues with test cases](#122-linking-external-issues-with-test-cases)
    - [(xxx) Generating test cases from Jira requirements](#xxx-generating-test-cases-from-jira-requirements)
  - [Importing test cases from other tools](#importing-test-cases-from-other-tools)
    - [(39) Qase CSV - old format](#39-qase-csv---old-format)
    - [(38) Qase CSV - custom fields](#38-qase-csv---custom-fields)
    - [(13) Qase CSV - bulk update](#13-qase-csv---bulk-update)
    - [(12) Qase CSV - suites](#12-qase-csv---suites)
    - [(11) Qase CSV - fields](#11-qase-csv---fields)
    - [(10) Qase CSV - steps](#10-qase-csv---steps)
    - [(9) Qase CSV - introduction](#9-qase-csv---introduction)
    - [(119) Submitting a case for review](#119-submitting-a-case-for-review)
    - [(118) Peer Reviews](#118-peer-reviews)
    - [(120) Using AI to generate test cases](#120-using-ai-to-generate-test-cases)
    - [(78) Project - overview](#78-project---overview)
    - [(81) Project - archive/delete](#81-project---archivedelete)
    - [(80) Project settings - access control](#80-project-settings---access-control)
    - [(77) User group - create](#77-user-group---create)
    - [(87) Groups - view and edit](#87-groups---view-and-edit)
    - [(88) Groups - delete](#88-groups---delete)
    - [(96) Milestone](#96-milestone)
    - [(67) Test case - mute](#67-test-case---mute)
    - [Test Plans and Test Runs](#test-plans-and-test-runs)
    - [(76) Test plan - edit](#76-test-plan---edit)
    - [(75) Test plan - delete](#75-test-plan---delete)
    - [(74) Test plan - export](#74-test-plan---export)
    - [(72) Test plan - create manual run](#72-test-plan---create-manual-run)
    - [(71) Test plan - Create](#71-test-plan---create)
- [Defects and Integration](#defects-and-integration)
  - [(51) Defect - create](#51-defect---create)
  - [(53) Defect - export](#53-defect---export)
  - [(54) Defect - link/create external issue](#54-defect---linkcreate-external-issue)
- [Test run](#test-run)
  - [(59) Test run - starting a test run](#59-test-run---starting-a-test-run)
  - [() Test run - total vs elapsed time](#-test-run---total-vs-elapsed-time)
  - [(62) Test run - assignment](#62-test-run---assignment)
  - [(61) Test run - defects tab](#61-test-run---defects-tab)
  - [(60) Test run - team stats tab](#60-test-run---team-stats-tab)
  - [(52) Test run - share report](#52-test-run---share-report)
  - [(63) Test run - link external issue](#63-test-run---link-external-issue)
  - [Test run settings: Explained](#test-run-settings-explained)
    - [(49) Test run settings - auto complete](#49-test-run-settings---auto-complete)
    - [(48) Test run settings - allow add results to completed test runs](#48-test-run-settings---allow-add-results-to-completed-test-runs)
    - [(46) Test run settings - fail case on step fail](#46-test-run-settings---fail-case-on-step-fail)
    - [(44) Test run settings - assignee result lock](#44-test-run-settings---assignee-result-lock)
    - [(35) Test run settings - default create/attach defect checkbox](#35-test-run-settings---default-createattach-defect-checkbox)
    - [(33) Test run settings - fast pass](#33-test-run-settings---fast-pass)
    - [(8) Test run settings - auto assignee](#8-test-run-settings---auto-assignee)
    - [(1) Test run settings - autopass](#1-test-run-settings---autopass)
- [Other Integrations & API](#other-integrations--api)
  - [(18) Github - qase-run-link](#18-github---qase-run-link)
  - [(7) API - attachments](#7-api---attachments)
  - [(5) API - intro](#5-api---intro)
  - [(14) Token - user vs app difference](#14-token---user-vs-app-difference)
- [Non-Member Assets](#non-member-assets)
  - [Billing and Invoices](#billing-and-invoices)
    - [(69) Billing - invoices](#69-billing---invoices)
  - [Other Misc](#other-misc)
    - [(70) Users - Invite](#70-users---invite)

---

> We need to cover all the permissions of the QA Member role in this learning path.

## User is invited to the workspace and they sign up.

#### (103) What is a workspace?
> Discuss the difference between account and workspace. Each account is uniquely identified by email. Each user can be part of multiple workspaces. Explain the concept of ownership.

#### (104) Joining your workspace
> 

#### (104) Accidental signup?
> User accidentally signs up for a new workspace instead of joining their company workspace.

#### (30) Issue - this invite is for another user
> This error occurs when a user tries to join a workspace, but they are signed in with a different email than the one they were invited with. Explain how to resolve this issue by signing out and signing in with the correct email.

#### (xx) Sign up process when teams use SSO and SCIM
> The process is straightforward, they'll just need to use the SSO sign-in page instead of the regular sign-up page.


---

## User after signing up, lands on the Project Page.

#### (68) Finding your way around the workspace
#### (102) Personalize: Picture and theme


#### (xx) Help is just a click away!
> Introduce the Help Center at this stage. Because, they'll want to know where to find help if they need it.

---

## Introduction to Roles

> Introduce users to Roles and role permissions. Explain who can do what within the workspace.
#### (106) Who's Who in Your Workspace?
#### (107) What's my role?

---

## General Workflow (Cases → Results → Defects)

> Introduce the general workflow of a QA Member in Qase, which involves creating test cases, executing them, and filing defects.
#### (83) What's a project?
#### (109) Organizing with test suites
#### (110) Creating (quick) test cases
#### (111) Anatomy of a test case
#### (112) Executing your tests
#### (113) Filing your first defect

---

## Repository Management

> User now understands basics and wants to learn about repository management. Use the "Task Tides" project** (theme: task management productivity app). In the asset, introduce the tools covered in the following videos, along with the theme. Keep this section very short.

#### (114) Repository management: TASKTIDES
> In this module, we will introduce an example project, Task Tides: an imaginary productivity and task management application. Throughout the series, we’ll use Task Tides to demonstrate key features and provide a consistent theme for our videos.

#### (115) Repository: tree vs folder view
> Large repositories benefit from folder view for quicker loading times
  
#### (116) Bulk deletion in the repository
> Demonstrate how suite deletion is different from case deletion and a caution about deleting suites with cases.

#### (117) Search and Filters
> Mention shortcut about CFS - Cases, Filters, and Suites.
  
#### (89) Trash bin

### Shared Steps
#### (86) Save time with Shared steps
> Talks about creation of new shared step, converting regular steps and deletion.

### System fields: Modify
#### (21) Modifying system fields
#### (19) Understanding the automation status field

### Custom fields: create, edit, and delete
#### (28) Custom fields - distribution widget
#### (27) System fields - results status
#### (26) Custom fields - QQL
#### (25) Custom fields - API
#### (23) Custom fields - order
#### (22) Custom fields - create

### Parameters


### Tags
#### (99) Workspace - tags

### Integrations: Repository
#### (122) Linking external issues with test cases
#### (xxx) Generating test cases from Jira requirements

### Importing test cases from other tools
> The following assets will cover importing process for teams migrating from other tools, or a spreadsheet software.

#### (39) Qase CSV - old format
#### (38) Qase CSV - custom fields
#### (13) Qase CSV - bulk update
#### (12) Qase CSV - suites
#### (11) Qase CSV - fields
#### (10) Qase CSV - steps
#### (9) Qase CSV - introduction


#### (119) Submitting a case for review
> This is for self and manager review

#### (118) Peer Reviews

#### (120) Using AI to generate test cases
> Demonstrate test case generation using copy-paste text.


#### (78) Project - overview
#### (81) Project - archive/delete
#### (80) Project settings - access control


#### (77) User group - create
#### (87) Groups - view and edit
#### (88) Groups - delete

#### (96) Milestone
#### (67) Test case - mute

#### Test Plans and Test Runs

#### (76) Test plan - edit
#### (75) Test plan - delete
#### (74) Test plan - export
#### (72) Test plan - create manual run
#### (71) Test plan - Create


## Defects and Integration

#### (51) Defect - create
#### (53) Defect - export
#### (54) Defect - link/create external issue



## Test run

#### (59) Test run - starting a test run
#### () Test run - total vs elapsed time
#### (62) Test run - assignment
#### (61) Test run - defects tab
#### (60) Test run - team stats tab
#### (52) Test run - share report
#### (63) Test run - link external issue


### Test run settings: Explained

#### (49) Test run settings - auto complete
#### (48) Test run settings - allow add results to completed test runs
#### (46) Test run settings - fail case on step fail
#### (44) Test run settings - assignee result lock
#### (35) Test run settings - default create/attach defect checkbox
#### (33) Test run settings - fast pass
#### (8) Test run settings - auto assignee
#### (1) Test run settings - autopass


## Other Integrations & API
#### (18) Github - qase-run-link
#### (7) API - attachments
#### (5) API - intro
#### (14) Token - user vs app difference

---

# Non-Member Assets

## Billing and Invoices
#### (69) Billing - invoices


## Other Misc
#### (70) Users - Invite

