---
title: "About the Handbook"
source_url: "https://handbook.gitlab.com/handbook/about/"
scraped_at: "2026-09-05"
doc_id: "about-the-handbook"
---

# About the Handbook

## History of the handbook

The handbook started when GitLab was a company of just ten people to make sharing information efficient and easy.
We knew that future GitLab team-members wouldn’t be able to see emails about process changes that were being sent before they joined and that most of the people who would eventually join GitLab likely hadn’t even heard of us yet.
The handbook was our way of ensuring that all of our company information was accessible to everyone regardless of when they became part of the team.

## Advantages

At GitLab our handbook is extensive and keeping it relevant is an important part of everyone’s job.
It is a vital part of who we are and how we communicate.
We established these processes because we saw these benefits:

1. Reading is much faster than listening.
2. Reading is async, you don’t have to interrupt someone or wait for them to become available.
3. Talent Acquisition is easier if people can see what we stand for and how we operate.
4. Retention is better if people know what they are getting into before they join.
5. On-boarding is easier if you can find all relevant information spelled out.
6. Teamwork is easier if you can read how other parts of the company work.
7. Discussing changes is easier if you can read what the current process is.
8. Communicating change is easier if you can just point to the diff.
9. Everyone can contribute to it by proposing a change via a merge request.

One common concern newcomers to the handbook express is that the strict documentation makes the company more rigid.
In fact, writing down our current process in the handbook has the effect of empowering contributors to propose change.
As a result, this handbook is far from rigid. You only need to look at the [handbook commits list](https://gitlab.com/gitlab-com/content-sites/handbook/-/commits/main) to see the evidence. Every attempt is made to document guidelines and processes in the handbook. However, it is not possible to document every possible situation or scenario that could potentially occur. Just because something is not yet in the handbook does not mean that it is allowed. GitLab will review each team member’s concern or situation based on local laws to determine the best outcome and then update the handbook accordingly. If you have questions, please discuss with your manager or contact the [People Success](https://handbook.gitlab.com/handbook/people-group/) team.

## Handbook Interpretation

The handbook is subject to interpretation. We do our best to be as clear as possible to minimize confusion and/or misinterpretation. We also recognize that we have a global audience and that may bring different interpretations. If you have any questions or need further clarification please check with the content owner of the page. When in doubt please reach out and ask.

**Remember that [everything is in draft](https://handbook.gitlab.com/handbook/values/#everything-is-in-draft) at GitLab and subject to change, this includes our handbook.**

## Count handbook pages

It’s easy to see that the handbook is large, but have you ever wondered just *how* large?
The handbook is over *two* *thousand* pages long. That’s a lot of good info!

### Historical Word and Page Counts

#### about.gitlab.com/handbook

| **Date** | **Word Count** | **Page Count** | **Notes** |
| --- | --- | --- | --- |
| 2018-01-01 | 298,806 | 228 |  |
| 2018-10-01 | 427,929 | 335 |  |
| 2019-01-01 | 520,519 | 439 |  |
| 2019-04-01 | 656,668 | 586 |  |
| 2019-07-01 | 818,064 | 766 |  |
| 2019-10-01 | 987,397 | 884 |  |
| 2020-01-01 | 1,204,642 | 1,035 |  |
| 2020-04-01 | 1,491,017 | 1,222 |  |
| 2020-07-01 | 1,851,350 | 1,488 |  |
| 2020-10-01 | 2,166,627 | 1,759 |  |
| 2021-01-01 | 2,410,554 | 1,914 |  |
| 2021-04-01 | 2,615,372 | 2,056 |  |
| 2021-07-01 | 2,956,781 | 2,271 |  |
| 2021-10-01 | 3,138,952 | 2,355 |  |
| 2022-01-01 | 3,280,108 | 2,395 |  |
| 2022-04-01 | 3,474,993 | 2,553 |  |
| 2022-07-01 | 3,628,280 | 2,641 |  |
| 2022-10-01 | 3,732,384 | 2,724 |  |
| 2023-01-01 | 3,732,186 | 2,722 | ⬅️ Last entry before migration |
| 2023-07-01 | 3,905,979 | 2,743 |  |
| 2023-10-01 | 3,478,407 | 2,306 |  |
| 2023-12-22 | 0 | 0 | ⬅️ Handbook Migration Complete |

#### handbook.gitlab.com/handbook

| **Date** | **Word Count** | **Page Count** | **Notes** |
| --- | --- | --- | --- |
| 2023-07-01 | 150,732 | 133 |  |
| 2023-10-01 | 1,909,139 | 1,403 |  |
| 2024-01-01 | 3,631,360 | 3,003 | ⬅️ Migration Completed |
| 2025-01-03 | 5,129,952 | 3,823 |  |
| 2025-12-11 | 5,129,807 | 4,022 |  |
| 2026-01-01 | 5,137,908 | 4,040 |  |
| 2026-09-04 | 3,981,243 | 3,294 | ⬅️ Hugo generated Live Count |

### Methodology

Word and page counts are determined through a simple two-step process:

1. Count the number of words in the handbook. This can be done by running `find sites/handbook/source/handbook -type f -name "*.md" -o -name "*.md.erb" | xargs wc -w` from the root of the repository.
2. Count the number of pages in the handbook. This can be done by running `grep -l -r "\" * | wc -l` from the root of the repository.

Note: If you need to go back to an earlier version of the handbook, use `` git checkout `git rev-list -n 1 --first-parent --before="2021-07-02 00:00" master` ``  specifying the next day after the day you want.

## View Statistics

On this page you can see handbook trends and discover popular pages that you may not know about.

GitLab uses [Snowplow](https://handbook.gitlab.com/handbook/enterprise-data/platform/snowplow/) to track handbook usage; the information can be viewed on [Tableau](https://10az.online.tableau.com/#/site/gitlab/views/PDGitlabHandbookPageTraffic/GitLabHandbookTraffic).

## More about the handbook

We’ve gathered *some* information about the handbook here, but there’s still more elsewhere.

* [Handbook usage](https://handbook.gitlab.com/handbook/about/handbook-usage/)
* [Handbook editing examples](https://handbook.gitlab.com/handbook/about/editing-handbook/practical-handbook-edits/)

---

##### [Content Websites](https://handbook.gitlab.com/handbook/about/maintenance/)

Overview This area has traditionally been referred to as “the handbook”, but over time …

##### [Contributing to the Handbook](https://handbook.gitlab.com/handbook/about/contributing/)

Basic information on contributing to the GitLab Handbook.

##### [Editing the Handbook](https://handbook.gitlab.com/handbook/about/editing-handbook/)

Information on how to edit the handbook including tips and troubleshooting.

##### [GitLab Handbook Usage](https://handbook.gitlab.com/handbook/about/handbook-usage/)

About how GitLab uses the handbook.

##### [Handbook Changelog](https://handbook.gitlab.com/handbook/about/changelog/)

The last 100 Merge Requests to the Handbook

##### [Handbook Direction](https://handbook.gitlab.com/handbook/about/direction/)

Overview The GitLab Handbook is the single source of truth for how we operate at GitLab, including …

##### [Handbook Escalation](https://handbook.gitlab.com/handbook/about/escalation/)

For information on team members’ roles and responsibilities, see Content Websites page. …

##### [Handbook Style Guide](https://handbook.gitlab.com/handbook/about/style-guide/)

GitLab’s general communications practices are detailed at GitLab Communication, but beyond …

Last modified March 7, 2025: [Fix broken links (`b1d67d8e`)](https://gitlab.com/gitlab-com/content-sites/handbook/commit/b1d67d8e)

[View page source](https://gitlab.com/gitlab-com/content-sites/handbook/blob/main/content/handbook/about/_index.md)
-
[Edit this page](https://gitlab.com/-/ide/project/gitlab-com/content-sites/handbook/edit/main/-/content/handbook/about/_index.md)
-
please [contribute](https://handbook.gitlab.com/handbook/about/contributing/).
[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-sa/4.0/)
